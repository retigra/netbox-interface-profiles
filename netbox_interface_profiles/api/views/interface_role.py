"""
InterfaceRole viewset for netbox interface profiles API.
"""

from netbox.api.viewsets import NetBoxModelViewSet

from ... import filtersets
from ...models import InterfaceRole
from ..serializers import InterfaceRoleSerializer


class InterfaceRoleViewSet(NetBoxModelViewSet):
    """API viewset for InterfaceRole."""

    queryset = InterfaceRole.objects.all()
    serializer_class = InterfaceRoleSerializer
    filterset_class = filtersets.InterfaceRoleFilterSet
