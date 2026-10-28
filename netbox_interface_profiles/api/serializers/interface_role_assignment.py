"""
InterfaceRoleAssignment serializer for netbox interface profiles API.
"""

from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ...models import InterfaceRoleAssignment


class InterfaceRoleAssignmentSerializer(NetBoxModelSerializer):
    """Serializer for InterfaceRoleAssignment."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_interface_profiles-api:interfaceroleassignment-detail"
    )

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
