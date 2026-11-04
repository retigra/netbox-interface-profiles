"""
Interface configuration viewset for interface profiles API.
"""

from dcim.models import Interface
from django.db.models import Prefetch
from netbox.api.viewsets import BaseViewSet
from rest_framework import mixins

from ... import filtersets
from ...models import InterfaceRoleAssignment
from ..serializers import InterfaceConfigSerializer


class InterfaceConfigViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, BaseViewSet):
    """Read-only API endpoint returning the interface role and rendered configuration of interfaces.

    Objects are interfaces, looked up by interface ID. Requires permission to view the interfaces; the role is
    only returned when the user may also view the interface's role assignment.
    """

    queryset = Interface.objects.select_related(
        "device__site",
        "device__platform",
        "device__device_type",
        "device__role",
        "device__tenant",
        "cable",
    ).prefetch_related("tags", "device__tags")
    serializer_class = InterfaceConfigSerializer
    filterset_class = filtersets.InterfaceConfigFilterSet

    def get_queryset(self):
        assignments = InterfaceRoleAssignment.objects.restrict(self.request.user, "view").select_related(
            "interface_role__group"
        )
        return super().get_queryset().prefetch_related(Prefetch("role_assignment", queryset=assignments))
