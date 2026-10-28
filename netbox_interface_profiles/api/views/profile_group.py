"""
ProfileGroup viewset for netbox interface profiles API.
"""

from netbox.api.viewsets import NetBoxModelViewSet

from ... import filtersets
from ...models import ProfileGroup
from ..serializers import ProfileGroupSerializer


class ProfileGroupViewSet(NetBoxModelViewSet):
    """API viewset for ProfileGroup."""

    queryset = ProfileGroup.objects.all()
    serializer_class = ProfileGroupSerializer
    filterset_class = filtersets.ProfileGroupFilterSet
