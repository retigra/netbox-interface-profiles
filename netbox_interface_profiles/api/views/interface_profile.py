"""
InterfaceProfile viewset for netbox interface profiles API.
"""

from netbox.api.viewsets import NetBoxModelViewSet

from ... import filtersets
from ...models import InterfaceProfile
from ..serializers import InterfaceProfileSerializer


class InterfaceProfileViewSet(NetBoxModelViewSet):
    """API viewset for InterfaceProfile."""

    queryset = InterfaceProfile.objects.all()
    serializer_class = InterfaceProfileSerializer
    filterset_class = filtersets.InterfaceProfileFilterSet
