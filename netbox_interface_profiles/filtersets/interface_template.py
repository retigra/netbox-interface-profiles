"""
InterfaceTemplate filterset for netbox interface profiles.
"""

import django_filters
from dcim.models import Site, SiteGroup
from django.contrib.contenttypes.models import ContentType
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
    scope_site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        method="filter_scope_site",
        label="Site (ID)",
    )
    scope_site_group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        method="filter_scope_site_group",
        label="Site Group (ID)",
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
            "scope_site_id",
            "scope_site_group_id",
            "speed",
            "duplex",
            "mtu",
            "mode",
            "enabled",
            "poe_mode",
        )

    def filter_scope_site(self, queryset, name, value):
        if not value:
            return queryset
        ct = ContentType.objects.get_for_model(Site)
        ids = [obj.pk for obj in value]
        return queryset.filter(scope_type=ct, scope_id__in=ids)

    def filter_scope_site_group(self, queryset, name, value):
        if not value:
            return queryset
        ct = ContentType.objects.get_for_model(SiteGroup)
        ids = [obj.pk for obj in value]
        return queryset.filter(scope_type=ct, scope_id__in=ids)

    def search(self, queryset, name, value):
        """Support global keyword search against name and description fields."""
        if not value.strip():
            return queryset
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))
