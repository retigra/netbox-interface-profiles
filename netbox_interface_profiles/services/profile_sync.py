"""Synchronization logic for applying interface profile templates."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from typing import Any, cast

from dcim.models import Interface, Site, SiteGroup
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import NON_FIELD_ERRORS, FieldDoesNotExist, ValidationError
from django.db import transaction
from django.db.models import Case, Field, ForeignKey, IntegerField, ManyToManyField, Model, Q, Value, When
from ipam.models import VLAN
from utilities.exceptions import AbortRequest

from ..models import InterfaceProfileAssignment, InterfaceTemplate, ProfileSync, ProfileSyncChange

SYNC_SCALAR_FIELDS = (
    "enabled",
    "speed",
    "duplex",
    "mtu",
    "mode",
    "poe_mode",
)


def _get_matching_template(assignment: InterfaceProfileAssignment) -> InterfaceTemplate | None:
    """Return the best matching interface template for an assignment.

    Priority order: site-scoped > site-group-scoped > global (no scope).
    """
    interface = cast(Any, assignment.interface)
    site = interface.device.site
    site_group = getattr(site, "group", None)

    site_ct = ContentType.objects.get_for_model(Site)
    site_group_ct = ContentType.objects.get_for_model(SiteGroup)

    scope_q = Q(scope_type__isnull=True)  # global
    if site:
        scope_q |= Q(scope_type=site_ct, scope_id=site.pk)
    if site_group:
        scope_q |= Q(scope_type=site_group_ct, scope_id=site_group.pk)

    templates = (
        InterfaceTemplate.objects.filter(interface_profile=assignment.interface_profile)
        .filter(scope_q)
        .annotate(
            scope_priority=Case(
                When(scope_type=site_ct, then=Value(0)),
                When(scope_type=site_group_ct, then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            )
        )
    )

    return templates.order_by("scope_priority", "pk").first()


def _capture_tagged_vlans(interface) -> list[VLAN]:
    """Return tagged VLANs ordered consistently for comparison and display."""
    return list(interface.tagged_vlans.all().order_by("vid", "pk"))


def _build_diff(interface, template: InterfaceTemplate) -> dict[str, tuple[Any, Any]]:
    """Build a field diff between interface attributes and template-derived values."""
    changes: dict[str, tuple[Any, Any]] = {}

    for field in SYNC_SCALAR_FIELDS:
        desired = getattr(template, field)
        if desired == "":
            # A blank choice means no value, just like None
            desired = None
        if field != "enabled" and desired is None and not template.is_set_null(field):
            continue
        current = getattr(interface, field)
        if current != desired:
            changes[field] = (current, desired)

    if "mode" in changes and changes["mode"][1] is None:
        # NetBox only allows an untagged VLAN on interfaces with a mode
        if interface.untagged_vlan_id is not None:
            changes["untagged_vlan"] = (interface.untagged_vlan, None)
    elif template.untagged_vlan_vid is not None or template.is_set_null("untagged_vlan_vid"):
        desired_untagged = template.resolve_untagged_vlan(interface.device.site)
        current_untagged = interface.untagged_vlan
        if interface.untagged_vlan_id != getattr(desired_untagged, "pk", None):
            changes["untagged_vlan"] = (current_untagged, desired_untagged)

    desired_tagged = template.resolve_tagged_vlans(interface.device.site)
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


def _apply_diff(interface, changes: dict[str, tuple[Any, Any]], profile) -> None:
    """Apply a computed diff to the interface instance and related VLANs.

    Raises AbortRequest when the result is not a valid interface. NetBox views and the REST API show its
    message to the user and roll back the request, including the assignment that triggered the sync.
    """
    scalar_changed = False

    for field in SYNC_SCALAR_FIELDS:
        if field in changes:
            _, new_value = changes[field]
            setattr(interface, field, new_value)
            scalar_changed = True

    if "untagged_vlan" in changes:
        _, new_untagged = changes["untagged_vlan"]
        interface.untagged_vlan = new_untagged
        scalar_changed = True

    if scalar_changed:
        try:
            interface.full_clean()
        except ValidationError as exc:
            raise AbortRequest(
                f"Profile {profile} cannot be applied to {interface.device} {interface.name}: "
                f"{_format_validation_error(exc)}"
            ) from exc
        interface.save()

    if "tagged_vlans" in changes:
        _, new_tagged = changes["tagged_vlans"]
        interface.tagged_vlans.set(new_tagged)


def sync_assignment(assignment: InterfaceProfileAssignment, commit: bool = True) -> dict[str, tuple[Any, Any]]:
    """Synchronize one assignment and return changed fields with old/new values."""
    template = _get_matching_template(assignment)
    if template is None:
        return {}

    changes = _build_diff(assignment.interface, template)
    if commit and changes:
        _apply_diff(assignment.interface, changes, assignment.interface_profile)

    return changes


def run_profile_sync(sync: ProfileSync) -> list[ProfileSyncChange]:
    """Synchronize all assignments of a profile and record every interface that changed.

    Each change stores the serialized interface before and after synchronization, like NetBox's
    changelog does. A dry run applies the changes inside a transaction that is rolled back, so the
    recorded post-change data is exactly what a committed run would have saved.
    """
    assignments = (
        InterfaceProfileAssignment.objects.select_related(
            "interface__device__site",
            "interface_profile",
        )
        .prefetch_related("interface__tagged_vlans")
        .filter(interface_profile=sync.interface_profile)
        .order_by("interface__device__name", "interface__name", "pk")
    )

    changes: list[ProfileSyncChange] = []

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
            _apply_diff(interface, diff, sync.interface_profile)
            change = ProfileSyncChange(
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

    return ProfileSyncChange.objects.bulk_create(changes)


def _get_interface_field(name: str) -> Field | None:
    try:
        return cast(Any, Interface)._meta.get_field(name)
    except FieldDoesNotExist:
        return None


def describe_changes(changes: Iterable[ProfileSyncChange]) -> list[dict[str, Any]]:
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
