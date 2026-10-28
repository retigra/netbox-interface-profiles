"""
InterfaceRoleAssignment filterset for netbox interface profiles.
"""

import django_filters
from dcim.models import Device, Interface
from netbox.filtersets import NetBoxModelFilterSet

from ..models import InterfaceRole, InterfaceRoleAssignment, RoleGroup


class InterfaceRoleAssignmentFilterSet(NetBoxModelFilterSet):
    """Filter set for InterfaceRoleAssignment."""

    interface_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface",
        queryset=Interface.objects.all(),
        label="Interface (ID)",
    )
    interface_role_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface_role",
        queryset=InterfaceRole.objects.all(),
        label="Interface Role (ID)",
    )
    interface_role_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface_role__group",
        queryset=RoleGroup.objects.all(),
        label="Role Group (ID)",
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface__device",
        queryset=Device.objects.all(),
        label="Device (ID)",
    )

    class Meta:
        model = InterfaceRoleAssignment
        fields = ("id", "interface_id", "interface_role_id", "interface_role_group_id", "device_id")

    def search(self, queryset, name, value):
        """Support global keyword search against related interface and role names."""
        if not value.strip():
            return queryset
        return (
            queryset.filter(interface__name__icontains=value)
            | queryset.filter(interface__device__name__icontains=value)
            | queryset.filter(interface_role__name__icontains=value)
        )
