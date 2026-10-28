"""
InterfaceRoleAssignment viewset for netbox interface profiles API.
"""

from netbox.api.viewsets import NetBoxModelViewSet

from ... import filtersets
from ...models import InterfaceRoleAssignment
from ..serializers import InterfaceRoleAssignmentSerializer


class InterfaceRoleAssignmentViewSet(NetBoxModelViewSet):
    """API viewset for InterfaceRoleAssignment."""

    queryset = InterfaceRoleAssignment.objects.select_related("interface", "interface_role")
    serializer_class = InterfaceRoleAssignmentSerializer
    filterset_class = filtersets.InterfaceRoleAssignmentFilterSet
