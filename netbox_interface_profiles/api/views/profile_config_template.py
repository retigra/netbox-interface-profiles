"""
ProfileConfigTemplate viewset for netbox interface profiles API.
"""

from netbox.api.features import SyncedDataMixin
from netbox.api.viewsets import NetBoxModelViewSet

from ... import filtersets
from ...models import ProfileConfigTemplate
from ..serializers import ProfileConfigTemplateSerializer


class ProfileConfigTemplateViewSet(SyncedDataMixin, NetBoxModelViewSet):
    """API viewset for ProfileConfigTemplate, including the /sync/ action."""

    queryset = ProfileConfigTemplate.objects.select_related(
        "interface_role", "platform", "device_type", "data_source", "data_file"
    ).prefetch_related("device_tags", "interface_tags")
    serializer_class = ProfileConfigTemplateSerializer
    filterset_class = filtersets.ProfileConfigTemplateFilterSet
