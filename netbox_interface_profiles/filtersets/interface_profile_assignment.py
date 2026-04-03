"""
InterfaceProfileAssignment filterset for netbox interface profiles.
"""

import django_filters
from dcim.models import Interface
from netbox.filtersets import NetBoxModelFilterSet

from ..models import InterfaceProfile, InterfaceProfileAssignment


class InterfaceProfileAssignmentFilterSet(NetBoxModelFilterSet):
    """Filter set for InterfaceProfileAssignment."""

    interface_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Interface.objects.all(),
        label="Interface (ID)",
    )
    interface_profile_id = django_filters.ModelMultipleChoiceFilter(
        queryset=InterfaceProfile.objects.all(),
        label="Interface Profile (ID)",
    )

    class Meta:
        model = InterfaceProfileAssignment
        fields = ("id", "interface_id", "interface_profile_id")

    def search(self, queryset, name, value):
        """Support global keyword search against related interface and profile names."""
        if not value.strip():
            return queryset
        return queryset.filter(interface__name__icontains=value) | queryset.filter(
            interface_profile__name__icontains=value
        )
