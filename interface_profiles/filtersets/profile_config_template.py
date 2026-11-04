"""
ProfileConfigTemplate filterset for interface profiles.
"""

import django_filters
from core.models import DataFile, DataSource
from dcim.models import DeviceType, Platform
from django.db.models import Q
from extras.models import Tag
from netbox.filtersets import NetBoxModelFilterSet

from ..models import InterfaceRole, ProfileConfigTemplate


class ProfileConfigTemplateFilterSet(NetBoxModelFilterSet):
    """Filter set for ProfileConfigTemplate."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    interface_role_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface_role",
        queryset=InterfaceRole.objects.all(),
        label="Interface Role (ID)",
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
    device_tag = django_filters.ModelMultipleChoiceFilter(
        field_name="device_tags__slug",
        queryset=Tag.objects.all(),
        to_field_name="slug",
        label="Device Tag (slug)",
    )
    device_tag_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device_tags",
        queryset=Tag.objects.all(),
        label="Device Tag (ID)",
    )
    interface_tag = django_filters.ModelMultipleChoiceFilter(
        field_name="interface_tags__slug",
        queryset=Tag.objects.all(),
        to_field_name="slug",
        label="Interface Tag (slug)",
    )
    interface_tag_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface_tags",
        queryset=Tag.objects.all(),
        label="Interface Tag (ID)",
    )
    data_source_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DataSource.objects.all(),
        label="Data Source (ID)",
    )
    data_file_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DataFile.objects.all(),
        label="Data File (ID)",
    )

    class Meta:
        model = ProfileConfigTemplate
        fields = (
            "id",
            "name",
            "description",
            "weight",
            "interface_role_id",
            "platform_id",
            "device_type_id",
            "debug",
            "auto_sync_enabled",
            "data_synced",
        )

    def search(self, queryset, name, value):
        """Support global keyword search against name and description fields."""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value) | Q(template_code__icontains=value)
        )
