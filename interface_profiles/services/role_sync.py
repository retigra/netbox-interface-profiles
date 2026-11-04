"""Synchronization logic for applying interface role templates."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from typing import Any, NoReturn, cast

from dcim.choices import InterfaceModeChoices
from dcim.models import Interface, Site, SiteGroup
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import NON_FIELD_ERRORS, FieldDoesNotExist, ValidationError
from django.db import transaction
from django.db.models import Case, Field, ForeignKey, IntegerField, ManyToManyField, Model, Q, QuerySet, Value, When
from ipam.models import VLAN
from utilities.exceptions import AbortRequest

from ..models import InterfaceRoleAssignment, InterfaceTemplate, RoleSync, RoleSyncChange
from ..models.interface_template import TEMPLATE_INTERFACE_FIELDS

# Interface fields set by _apply_diff() before the interface is validated and saved
SAVED_INTERFACE_FIELDS = (*TEMPLATE_INTERFACE_FIELDS.values(), "untagged_vlan", "qinq_svlan")


def get_matching_templates(interface, interface_role) -> QuerySet[InterfaceTemplate]:
    """Return the interface templates of a role that match an interface, the one that applies first.

    Priority order: site-scoped > site-group-scoped > global (no scope).
    """
    site = interface.device.site
    site_group_id = getattr(site, "group_id", None)

    site_ct = ContentType.objects.get_for_model(Site)
    site_group_ct = ContentType.objects.get_for_model(SiteGroup)

    scope_q = Q(scope_type__isnull=True)  # global
    if site:
        scope_q |= Q(scope_type=site_ct, scope_id=site.pk)
    if site_group_id:
        scope_q |= Q(scope_type=site_group_ct, scope_id=site_group_id)

    return (
        InterfaceTemplate.objects.filter(interface_role=interface_role)
        .filter(scope_q)
        .annotate(
            scope_priority=Case(
                When(scope_type=site_ct, then=Value(0)),
                When(scope_type=site_group_ct, then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            )
        )
        .order_by("scope_priority", "pk")
    )


def _get_matching_template(assignment: InterfaceRoleAssignment) -> InterfaceTemplate | None:
    """Return the interface template that applies to an assignment, if any."""
    return get_matching_templates(assignment.interface, assignment.interface_role).first()


def _capture_tagged_vlans(interface) -> list[VLAN]:
    """Return tagged VLANs ordered consistently for comparison and display."""
    return list(interface.tagged_vlans.all().order_by("vid", "pk"))


def _vlan_diff(changes: dict[str, tuple[Any, Any]], interface, field: str, desired: VLAN | None) -> None:
    """Record a change of a VLAN foreign key of the interface when it differs from the desired VLAN."""
    if getattr(interface, f"{field}_id") != getattr(desired, "pk", None):
        changes[field] = (getattr(interface, field), desired)


def _build_diff(interface, template: InterfaceTemplate) -> dict[str, tuple[Any, Any]]:
    """Build a field diff between interface attributes and template-derived values.

    Keys are interface field names. Foreign keys are compared and set by primary key.
    """
    changes: dict[str, tuple[Any, Any]] = {}

    for template_field, interface_field in TEMPLATE_INTERFACE_FIELDS.items():
        desired = getattr(template, cast(Any, InterfaceTemplate)._meta.get_field(template_field).attname)
        if desired in (None, ""):
            # Empty values leave the interface unchanged, unless the template clears the attribute
            if not template.is_set_null(template_field):
                continue
            field = cast(Any, Interface)._meta.get_field(interface_field)
            desired = None if field.null else ""
        current = getattr(interface, cast(Any, Interface)._meta.get_field(interface_field).attname)
        if current != desired:
            changes[interface_field] = (current, desired)

    site = interface.device.site
    mode = changes["mode"][1] if "mode" in changes else interface.mode
    mode_changed = "mode" in changes

    # NetBox only allows an untagged VLAN on interfaces with a mode
    if mode_changed and not mode:
        _vlan_diff(changes, interface, "untagged_vlan", None)
    elif template.untagged_vlan_vid is not None or template.is_set_null("untagged_vlan_vid"):
        _vlan_diff(changes, interface, "untagged_vlan", template.resolve_untagged_vlan(site))

    # NetBox only allows a service VLAN on Q-in-Q interfaces
    if template.qinq_svlan_vid is not None or template.is_set_null("qinq_svlan_vid"):
        _vlan_diff(changes, interface, "qinq_svlan", template.resolve_qinq_svlan(site))
    elif mode_changed and mode != InterfaceModeChoices.MODE_Q_IN_Q:
        _vlan_diff(changes, interface, "qinq_svlan", None)

    # Tagged VLANs are always applied: an empty list removes them. NetBox only allows them in the tagged mode, so
    # VIDs on an interface in another mode are left for _apply_diff() to reject.
    if mode == InterfaceModeChoices.MODE_TAGGED or template.tagged_vlans_vids:
        desired_tagged = template.resolve_tagged_vlans(site)
    else:
        desired_tagged = []
    current_tagged = _capture_tagged_vlans(interface)
    if {v.pk for v in current_tagged} != {v.pk for v in desired_tagged}:
        changes["tagged_vlans"] = (current_tagged, desired_tagged)

    return changes


def _format_validation_error(error: ValidationError) -> str:
    """Join the messages of a validation error, prefixing each with the label of its field."""
    if not hasattr(error, "error_dict"):
        return " ".join(error.messages)

    parts = []
    for name, messages in error.message_dict.items():
        field = _get_interface_field(name)
        text = " ".join(messages)
        parts.append(text if name == NON_FIELD_ERRORS or field is None else f"{field.verbose_name}: {text}")
    return "; ".join(parts)


def _apply_diff(interface, changes: dict[str, tuple[Any, Any]], role) -> None:
    """Apply a computed diff to the interface instance and related VLANs.

    Raises AbortRequest when the result is not a valid interface. NetBox views and the REST API show its
    message to the user and roll back the request, including the assignment that triggered the sync.
    """

    def abort(message: str, exc: Exception | None = None) -> NoReturn:
        raise AbortRequest(f"Role {role} cannot be applied to {interface.device} {interface.name}: {message}") from exc

    saved_changes = [field for field in SAVED_INTERFACE_FIELDS if field in changes]
    for field in saved_changes:
        _, new_value = changes[field]
        if isinstance(new_value, Model):
            setattr(interface, field, new_value)
        else:
            setattr(interface, cast(Any, Interface)._meta.get_field(field).attname, new_value)

    if saved_changes:
        try:
            interface.full_clean()
        except ValidationError as exc:
            abort(_format_validation_error(exc), exc)
        interface.save()

    if "tagged_vlans" in changes:
        _, new_tagged = changes["tagged_vlans"]
        if new_tagged and interface.mode != InterfaceModeChoices.MODE_TAGGED:
            abort(f"Tagged VLANs: Interface mode {interface.mode or 'none'} does not support tagged VLANs.")
        interface.tagged_vlans.set(new_tagged)


def sync_assignment(assignment: InterfaceRoleAssignment, commit: bool = True) -> dict[str, tuple[Any, Any]]:
    """Synchronize one assignment and return changed fields with old/new values."""
    template = _get_matching_template(assignment)
    if template is None:
        return {}

    changes = _build_diff(assignment.interface, template)
    if commit and changes:
        _apply_diff(assignment.interface, changes, assignment.interface_role)

    return changes


def run_role_sync(sync: RoleSync) -> list[RoleSyncChange]:
    """Synchronize all assignments of a role and record every interface that changed.

    Each change stores the serialized interface before and after synchronization, like NetBox's
    changelog does. A dry run applies the changes inside a transaction that is rolled back, so the
    recorded post-change data is exactly what a committed run would have saved.
    """
    assignments = (
        InterfaceRoleAssignment.objects.select_related(
            "interface__device__site",
            "interface_role",
        )
        .prefetch_related("interface__tagged_vlans")
        .filter(interface_role=sync.interface_role)
        .order_by("interface__device__name", "interface__name", "pk")
    )

    changes: list[RoleSyncChange] = []

    with transaction.atomic():
        for assignment in assignments:
            template = _get_matching_template(assignment)
            if template is None:
                continue

            interface = assignment.interface
            diff = _build_diff(interface, template)
            if not diff:
                continue

            prechange_data = interface.serialize_object()
            _apply_diff(interface, diff, sync.interface_role)
            change = RoleSyncChange(
                sync=sync,
                interface=interface,
                device_name=str(interface.device),
                interface_name=interface.name,
                prechange_data=prechange_data,
                postchange_data=interface.serialize_object(),
            )
            if change.diff():
                changes.append(change)

        if sync.dry_run:
            transaction.set_rollback(True)

    sync.interface_count = len(assignments)
    sync.save(update_fields=["interface_count"])

    return RoleSyncChange.objects.bulk_create(changes)


def _get_interface_field(name: str) -> Field | None:
    try:
        return cast(Any, Interface)._meta.get_field(name)
    except FieldDoesNotExist:
        return None


def describe_changes(changes: Iterable[RoleSyncChange]) -> list[dict[str, Any]]:
    """Resolve recorded interface snapshots into display rows, one per interface.

    Serialized data holds raw values (choice keys, related primary keys), so these are resolved
    to choice labels and related objects. Objects that no longer exist are shown by primary key.
    """
    diffs = [(change, change.diff()) for change in changes]

    # Collect related primary keys first, so each related model is queried only once
    related_pks: dict[type[Model], set[int]] = defaultdict(set)
    for _, diff in diffs:
        for name, values in diff.items():
            field = _get_interface_field(name)
            if isinstance(field, ForeignKey | ManyToManyField):
                for value in values:
                    related_pks[field.related_model].update(value if isinstance(value, list) else [value])
    related = {
        model: cast(Any, model).objects.in_bulk([pk for pk in pks if pk is not None])
        for model, pks in related_pks.items()
    }

    def resolve(field: Field | None, value: Any) -> Any:
        if value is None or field is None:
            return value
        if isinstance(field, ForeignKey | ManyToManyField):
            objects = related[field.related_model]

            def get_object(pk):
                return objects.get(pk, f"#{pk} (deleted)")

            if isinstance(value, list):
                return sorted((get_object(pk) for pk in value), key=lambda obj: (getattr(obj, "vid", 0), str(obj)))
            return get_object(value)
        if field.choices:
            return dict(field.flatchoices).get(value, value)
        return value

    rows = []
    for change, diff in diffs:
        attributes = []
        for name, (old, new) in diff.items():
            field = _get_interface_field(name)
            attributes.append(
                {
                    "label": field.verbose_name if field else name,
                    "old": resolve(field, old),
                    "new": resolve(field, new),
                }
            )
        rows.append({"change": change, "attributes": attributes})

    return rows
