"""
InterfaceProfile filterset for netbox interface profiles.
"""

import django_filters
from dcim.models import DeviceRole
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet

from ..models import InterfaceProfile, ProfileGroup


class InterfaceProfileFilterSet(NetBoxModelFilterSet):
    """Filter set for InterfaceProfile supporting name, description, group, and device_roles filters."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ProfileGroup.objects.all(),
        label="Group (ID)",
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name="group__slug",
        queryset=ProfileGroup.objects.all(),
        to_field_name="slug",
        label="Group (slug)",
    )
    device_roles = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceRole.objects.all(),
    )

    class Meta:
        model = InterfaceProfile
        fields = ("id", "name", "description", "group_id", "group", "device_roles")

    def search(self, queryset, name, value):
        """Support global keyword search against name and description fields."""
        if not value.strip():
            return queryset
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))
