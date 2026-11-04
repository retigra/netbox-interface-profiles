"""
InterfaceRoleAssignment serializer for interface profiles API.
"""

from dcim.api.serializers import InterfaceSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ...models import InterfaceRoleAssignment
from .interface_role import InterfaceRoleSerializer


class InterfaceRoleAssignmentSerializer(NetBoxModelSerializer):
    """Serializer for InterfaceRoleAssignment.

    The interface and role are written by ID (or by attributes, like other NetBox nested objects) and returned as
    nested objects.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:interface_profiles-api:interfaceroleassignment-detail"
    )
    interface = InterfaceSerializer(nested=True)
    interface_role = InterfaceRoleSerializer(nested=True)

    class Meta:
        model = InterfaceRoleAssignment
        fields = (
            "id",
            "url",
            "display",
            "interface",
            "interface_role",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "interface", "interface_role")
