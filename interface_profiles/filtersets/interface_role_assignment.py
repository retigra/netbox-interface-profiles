"""
InterfaceRoleAssignment filterset for interface profiles.
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
    interface_role = django_filters.ModelMultipleChoiceFilter(
        field_name="interface_role__name",
        queryset=InterfaceRole.objects.all(),
        to_field_name="name",
        label="Interface Role (name)",
    )
    interface_role_group = django_filters.ModelMultipleChoiceFilter(
        field_name="interface_role__group__slug",
        queryset=RoleGroup.objects.all(),
        to_field_name="slug",
        label="Role Group (slug)",
    )
    interface = django_filters.CharFilter(
        field_name="interface__name",
        label="Interface (name)",
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface__device",
        queryset=Device.objects.all(),
        label="Device (ID)",
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name="interface__device__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name)",
    )

    class Meta:
        model = InterfaceRoleAssignment
        fields = ("id",)

    def search(self, queryset, name, value):
        """Support global keyword search against related interface and role names."""
        if not value.strip():
            return queryset
        return (
            queryset.filter(interface__name__icontains=value)
            | queryset.filter(interface__device__name__icontains=value)
            | queryset.filter(interface_role__name__icontains=value)
        )
