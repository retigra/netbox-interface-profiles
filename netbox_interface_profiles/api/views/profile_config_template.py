"""
ProfileConfigTemplate viewset for netbox interface profiles API.
"""

from netbox.api.viewsets import NetBoxModelViewSet

from ... import filtersets
from ...models import ProfileConfigTemplate
from ..serializers import ProfileConfigTemplateSerializer


class ProfileConfigTemplateViewSet(NetBoxModelViewSet):
    """API viewset for ProfileConfigTemplate."""

    queryset = ProfileConfigTemplate.objects.prefetch_related("interface_profile", "device_type")
    serializer_class = ProfileConfigTemplateSerializer
    filterset_class = filtersets.ProfileConfigTemplateFilterSet
