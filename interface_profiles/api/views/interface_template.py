"""
InterfaceTemplate viewset for interface profiles API.
"""

from netbox.api.viewsets import NetBoxModelViewSet

from ... import filtersets
from ...models import InterfaceTemplate
from ..serializers import InterfaceTemplateSerializer


class InterfaceTemplateViewSet(NetBoxModelViewSet):
    """API viewset for InterfaceTemplate."""

    queryset = InterfaceTemplate.objects.select_related(
        "interface_role",
        "scope_type",
        "vrf",
        "vlan_translation_policy",
    ).prefetch_related("scope_sites", "scope_site_groups")
    serializer_class = InterfaceTemplateSerializer
    filterset_class = filtersets.InterfaceTemplateFilterSet
