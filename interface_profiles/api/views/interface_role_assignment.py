"""
InterfaceRoleAssignment viewset for interface profiles API.
"""

from netbox.api.viewsets import NetBoxModelViewSet

from ... import filtersets
from ...models import InterfaceRoleAssignment
from ..serializers import InterfaceRoleAssignmentSerializer


class InterfaceRoleAssignmentViewSet(NetBoxModelViewSet):
    """API viewset for InterfaceRoleAssignment."""

    queryset = InterfaceRoleAssignment.objects.select_related("interface__device", "interface_role__group")
    serializer_class = InterfaceRoleAssignmentSerializer
    filterset_class = filtersets.InterfaceRoleAssignmentFilterSet
