"""
ProfileConfigTemplate filterset for netbox interface profiles.
"""

import django_filters
from dcim.models import DeviceType, Platform
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet

from ..models import InterfaceProfile, InterfaceTemplate, ProfileConfigTemplate


class ProfileConfigTemplateFilterSet(NetBoxModelFilterSet):
    """Filter set for ProfileConfigTemplate."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    interface_profile_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface_template__interface_profile",
        queryset=InterfaceProfile.objects.all(),
        label="Interface Profile (ID)",
    )
    interface_template_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface_template",
        queryset=InterfaceTemplate.objects.all(),
        label="Interface Template (ID)",
    )
    platform_id = django_filters.ModelMultipleChoiceFilter(
        field_name="platform",
        queryset=Platform.objects.all(),
        label="Platform (ID)",
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device_type",
        queryset=DeviceType.objects.all(),
        label="Device Type (ID)",
    )

    class Meta:
        model = ProfileConfigTemplate
        fields = (
            "id",
            "name",
            "description",
            "interface_profile_id",
            "interface_template_id",
            "platform_id",
            "device_type_id",
        )

    def search(self, queryset, name, value):
        """Support global keyword search against name and description fields."""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value) | Q(template_code__icontains=value)
        )
