"""Signal handlers for interface profile assignments."""

from __future__ import annotations

from typing import Any, cast

from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import InterfaceProfileAssignment, InterfaceTemplate


def _get_matching_template(assignment: InterfaceProfileAssignment) -> InterfaceTemplate | None:
    """Return the best matching interface template for an assignment."""
    interface = cast(Any, assignment.interface)
    device = interface.device
    site_group_id = getattr(device.site, "group_id", None)

    templates = InterfaceTemplate.objects.filter(
        interface_profile=assignment.interface_profile,
    )

    if site_group_id:
        templates = templates.filter(Q(site_group_id=site_group_id) | Q(site_group__isnull=True))
    else:
        templates = templates.filter(site_group__isnull=True)

    return templates.order_by("site_group_id", "pk").first()


def _apply_template_attributes(assignment: InterfaceProfileAssignment, template: InterfaceTemplate) -> None:
    """Apply template attributes to the assigned interface."""
    interface = cast(Any, assignment.interface)
    site = interface.device.site

    scalar_fields = [
        "enabled",
        "speed",
        "duplex",
        "mtu",
        "mode",
        "poe_mode",
    ]

    changed = False
    for field in scalar_fields:
        value = getattr(template, field)
        if value is None:
            continue
        if getattr(interface, field) != value:
            setattr(interface, field, value)
            changed = True

    if template.untagged_vlan_vid is not None:
        untagged_vlan = template.resolve_untagged_vlan(site)
        if interface.untagged_vlan_id != getattr(untagged_vlan, "pk", None):
            interface.untagged_vlan = untagged_vlan
            changed = True

    if changed:
        interface.save()

    tagged_vlans = template.resolve_tagged_vlans(site)
    current_tagged_vlan_ids = set(interface.tagged_vlans.values_list("pk", flat=True))
    new_tagged_vlan_ids = {vlan.pk for vlan in tagged_vlans}
    if current_tagged_vlan_ids != new_tagged_vlan_ids:
        interface.tagged_vlans.set(tagged_vlans)


@receiver(post_save, sender=InterfaceProfileAssignment)
def apply_interface_template_on_assignment(
    sender,
    instance: InterfaceProfileAssignment,
    created: bool,
    **kwargs,
) -> None:
    """Apply a matching template whenever a profile assignment is created/updated."""
    if not created and kwargs.get("update_fields") == {"last_updated"}:
        return

    assignment = (
        InterfaceProfileAssignment.objects.select_related(
            "interface__device__site",
            "interface_profile",
        )
        .prefetch_related("interface__tagged_vlans")
        .get(pk=instance.pk)
    )

    template = _get_matching_template(assignment)
    if template is None:
        return

    _apply_template_attributes(assignment, template)
