"""Synchronization logic for applying interface profile templates."""

from __future__ import annotations

from typing import Any, cast

from django.db import transaction
from django.db.models import Q
from ipam.models import VLAN

from ..models import InterfaceProfile, InterfaceProfileAssignment, InterfaceTemplate

SYNC_SCALAR_FIELDS = (
    "enabled",
    "speed",
    "duplex",
    "mtu",
    "mode",
    "poe_mode",
)


def _get_matching_template(assignment: InterfaceProfileAssignment) -> InterfaceTemplate | None:
    """Return the best matching interface template for an assignment."""
    interface = cast(Any, assignment.interface)
    site_group_id = getattr(interface.device.site, "group_id", None)

    templates = InterfaceTemplate.objects.filter(interface_profile=assignment.interface_profile)
    if site_group_id:
        templates = templates.filter(Q(site_group_id=site_group_id) | Q(site_group__isnull=True))
    else:
        templates = templates.filter(site_group__isnull=True)

    return templates.order_by("site_group_id", "pk").first()


def _capture_tagged_vlans(interface) -> list[VLAN]:
    """Return tagged VLANs ordered consistently for comparison and display."""
    return list(interface.tagged_vlans.all().order_by("vid", "pk"))


def _build_diff(interface, template: InterfaceTemplate) -> dict[str, tuple[Any, Any]]:
    """Build a field diff between interface attributes and template-derived values."""
    changes: dict[str, tuple[Any, Any]] = {}

    for field in SYNC_SCALAR_FIELDS:
        desired = getattr(template, field)
        if field != "enabled" and desired is None:
            continue
        current = getattr(interface, field)
        if current != desired:
            changes[field] = (current, desired)

    if template.untagged_vlan_vid is not None:
        desired_untagged = template.resolve_untagged_vlan(interface.device.site)
        current_untagged = interface.untagged_vlan
        if interface.untagged_vlan_id != getattr(desired_untagged, "pk", None):
            changes["untagged_vlan"] = (current_untagged, desired_untagged)

    desired_tagged = template.resolve_tagged_vlans(interface.device.site)
    current_tagged = _capture_tagged_vlans(interface)
    if {v.pk for v in current_tagged} != {v.pk for v in desired_tagged}:
        changes["tagged_vlans"] = (current_tagged, desired_tagged)

    return changes


def _apply_diff(interface, changes: dict[str, tuple[Any, Any]]) -> None:
    """Apply a computed diff to the interface instance and related VLANs."""
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
        _apply_diff(assignment.interface, changes)

    return changes


def sync_assignments_for_profile(
    profile: InterfaceProfile,
    dry_run: bool,
) -> list[dict[str, Any]]:
    """Synchronize all assignments for a profile and return per-field diff rows."""
    assignments = (
        InterfaceProfileAssignment.objects.select_related(
            "interface__device__site",
            "interface_profile",
        )
        .prefetch_related("interface__tagged_vlans")
        .filter(interface_profile=profile)
        .order_by("interface__device__name", "interface__name", "pk")
    )

    rows: list[dict[str, Any]] = []

    with transaction.atomic():
        for assignment in assignments:
            changes = sync_assignment(assignment=assignment, commit=True)
            interface = assignment.interface
            for field, (old_value, new_value) in changes.items():
                rows.append(
                    {
                        "interface": interface,
                        "field": field,
                        "old": old_value,
                        "new": new_value,
                    }
                )

        if dry_run:
            transaction.set_rollback(True)

    return rows


def format_diff_value(value: Any) -> str:
    """Format a changed value for display in job output."""
    if value is None:
        return "-"

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, list):
        if not value:
            return "-"
        return ", ".join(format_diff_value(item) for item in value)

    if isinstance(value, VLAN):
        return f"{value.vid} ({value.name})"

    return str(value)
