"""
RoleGroup viewset for netbox interface profiles API.
"""

from netbox.api.viewsets import NetBoxModelViewSet

from ... import filtersets
from ...models import RoleGroup
from ..serializers import RoleGroupSerializer


class RoleGroupViewSet(NetBoxModelViewSet):
    """API viewset for RoleGroup."""

    queryset = RoleGroup.objects.all()
    serializer_class = RoleGroupSerializer
    filterset_class = filtersets.RoleGroupFilterSet
