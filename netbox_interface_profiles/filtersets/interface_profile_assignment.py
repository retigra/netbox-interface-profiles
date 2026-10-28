"""
InterfaceProfileAssignment filterset for netbox interface profiles.
"""

import django_filters
from dcim.models import Device, Interface
from netbox.filtersets import NetBoxModelFilterSet

from ..models import InterfaceProfile, InterfaceProfileAssignment, ProfileGroup


class InterfaceProfileAssignmentFilterSet(NetBoxModelFilterSet):
    """Filter set for InterfaceProfileAssignment."""

    interface_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface",
        queryset=Interface.objects.all(),
        label="Interface (ID)",
    )
    interface_profile_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface_profile",
        queryset=InterfaceProfile.objects.all(),
        label="Interface Profile (ID)",
    )
    interface_profile_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface_profile__group",
        queryset=ProfileGroup.objects.all(),
        label="Profile Group (ID)",
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface__device",
        queryset=Device.objects.all(),
        label="Device (ID)",
    )

    class Meta:
        model = InterfaceProfileAssignment
        fields = ("id", "interface_id", "interface_profile_id", "interface_profile_group_id", "device_id")

    def search(self, queryset, name, value):
        """Support global keyword search against related interface and profile names."""
        if not value.strip():
            return queryset
        return (
            queryset.filter(interface__name__icontains=value)
            | queryset.filter(interface__device__name__icontains=value)
            | queryset.filter(interface_profile__name__icontains=value)
        )
