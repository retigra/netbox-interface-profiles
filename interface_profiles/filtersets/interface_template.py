"""
InterfaceTemplate filterset for interface profiles.
"""

import django_filters
from dcim.choices import InterfaceDuplexChoices, InterfaceModeChoices, InterfacePoEModeChoices, InterfacePoETypeChoices
from dcim.models import Site, SiteGroup
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from ipam.models import VRF, VLANTranslationPolicy
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filters import ContentTypeFilter, MultiValueNumberFilter

from ..models import InterfaceRole, InterfaceTemplate


class InterfaceTemplateFilterSet(NetBoxModelFilterSet):
    """Filter set for InterfaceTemplate supporting various template attribute filters."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    interface_description = django_filters.CharFilter(lookup_expr="icontains")
    interface_role_id = django_filters.ModelMultipleChoiceFilter(
        field_name="interface_role",
        queryset=InterfaceRole.objects.all(),
        label="Interface Role (ID)",
    )
    interface_role = django_filters.ModelMultipleChoiceFilter(
        field_name="interface_role__name",
        queryset=InterfaceRole.objects.all(),
        to_field_name="name",
        label="Interface Role (name)",
    )
    scope_type = ContentTypeFilter()
    scope_site_id = MultiValueNumberFilter(method="filter_scope_site", label="Site (ID)")
    scope_site_group_id = MultiValueNumberFilter(method="filter_scope_site_group", label="Site Group (ID)")
    is_global = django_filters.BooleanFilter(
        field_name="scope_type",
        lookup_expr="isnull",
        label="Global (no scope)",
    )
    duplex = django_filters.MultipleChoiceFilter(choices=InterfaceDuplexChoices, null_value=None)
    mode = django_filters.MultipleChoiceFilter(choices=InterfaceModeChoices, null_value=None)
    poe_mode = django_filters.MultipleChoiceFilter(choices=InterfacePoEModeChoices, null_value=None)
    poe_type = django_filters.MultipleChoiceFilter(choices=InterfacePoETypeChoices, null_value=None)
    vrf_id = django_filters.ModelMultipleChoiceFilter(
        field_name="vrf",
        queryset=VRF.objects.all(),
        label="VRF (ID)",
    )
    vlan_translation_policy_id = django_filters.ModelMultipleChoiceFilter(
        field_name="vlan_translation_policy",
        queryset=VLANTranslationPolicy.objects.all(),
        label="VLAN translation policy (ID)",
    )
    tagged_vlan_vid = django_filters.NumberFilter(
        method="filter_tagged_vlan_vid",
        label="Tagged VLAN VID",
    )

    class Meta:
        model = InterfaceTemplate
        fields = (
            "id",
            "name",
            "description",
            "enabled",
            "mgmt_only",
            "speed",
            "mtu",
            "untagged_vlan_vid",
            "qinq_svlan_vid",
            "set_null_interface_description",
            "set_null_speed",
            "set_null_duplex",
            "set_null_mtu",
            "set_null_mode",
            "set_null_poe_mode",
            "set_null_poe_type",
            "set_null_vrf",
            "set_null_vlan_translation_policy",
            "set_null_untagged_vlan_vid",
            "set_null_qinq_svlan_vid",
        )

    def filter_scope_site(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(scope_type=ContentType.objects.get_for_model(Site), scope_id__in=value)

    def filter_scope_site_group(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(scope_type=ContentType.objects.get_for_model(SiteGroup), scope_id__in=value)

    def filter_tagged_vlan_vid(self, queryset, name, value):
        if value is None:
            return queryset
        return queryset.filter(tagged_vlans_vids__contains=[int(value)])

    def search(self, queryset, name, value):
        """Support global keyword search against name and description fields."""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value) | Q(interface_description__icontains=value)
        )
