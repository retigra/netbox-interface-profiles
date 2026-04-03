"""
InterfaceProfile filterset for netbox interface profiles.
"""

import django_filters
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet

from ..models import InterfaceProfile


class InterfaceProfileFilterSet(NetBoxModelFilterSet):
    """Filter set for InterfaceProfile supporting name and description filters."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = InterfaceProfile
        fields = ("id", "name", "description")

    def search(self, queryset, name, value):
        """Support global keyword search against name and description fields."""
        if not value.strip():
            return queryset
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))
