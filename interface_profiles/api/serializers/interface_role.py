"""
InterfaceRole serializer for interface profiles API.
"""

from dcim.api.serializers import DeviceRoleSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ...models import InterfaceRole
from .role_group import RoleGroupSerializer


class InterfaceRoleSerializer(NetBoxModelSerializer):
    """Serializer for InterfaceRole."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:interface_profiles-api:interfacerole-detail")
    group = RoleGroupSerializer(nested=True, required=False, allow_null=True)
    device_roles = DeviceRoleSerializer(many=True, nested=True, required=False)

    class Meta:
        model = InterfaceRole
        fields = (
            "id",
            "name",
            "url",
            "display",
            "description",
            "group",
            "device_roles",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "name", "url", "display", "description", "group")
