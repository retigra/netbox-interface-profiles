"""
InterfaceTemplate filterset for netbox interface profiles.
"""

import django_filters
from dcim.models import SiteGroup
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet

from ..models import InterfaceProfile, InterfaceTemplate


class InterfaceTemplateFilterSet(NetBoxModelFilterSet):
    """Filter set for InterfaceTemplate supporting various template attribute filters."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    interface_profile_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface_profile",
        queryset=InterfaceProfile.objects.all(),
    )
    site_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name="site_group",
        queryset=SiteGroup.objects.all(),
    )
    speed = django_filters.NumberFilter()
    duplex = django_filters.ChoiceFilter(
        choices=(
            ("auto", "Auto"),
            ("half", "Half"),
            ("full", "Full"),
        )
    )
    mtu = django_filters.NumberFilter()
    mode = django_filters.ChoiceFilter(
        choices=(
            ("access", "Access"),
            ("tagged", "Tagged"),
            ("tagged-all", "Tagged All"),
        )
    )
    enabled = django_filters.BooleanFilter()
    poe_mode = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = InterfaceTemplate
        fields = (
            "id",
            "name",
            "description",
            "interface_profile_id",
            "site_group_id",
            "speed",
            "duplex",
            "mtu",
            "mode",
            "enabled",
            "poe_mode",
        )

    def search(self, queryset, name, value):
        """Support global keyword search against name and description fields."""
        if not value.strip():
            return queryset
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))
