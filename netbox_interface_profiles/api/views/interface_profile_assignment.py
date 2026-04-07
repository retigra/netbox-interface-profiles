"""
InterfaceProfileAssignment viewset for netbox interface profiles API.
"""

from netbox.api.viewsets import NetBoxModelViewSet

from ... import filtersets
from ...models import InterfaceProfileAssignment
from ..serializers import InterfaceProfileAssignmentSerializer


class InterfaceProfileAssignmentViewSet(NetBoxModelViewSet):
    """API viewset for InterfaceProfileAssignment."""

    queryset = InterfaceProfileAssignment.objects.select_related("interface", "interface_profile")
    serializer_class = InterfaceProfileAssignmentSerializer
    filterset_class = filtersets.InterfaceProfileAssignmentFilterSet
