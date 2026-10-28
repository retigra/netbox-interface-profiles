"""
InterfaceProfile serializer for netbox interface profiles API.
"""

from dcim.api.serializers import DeviceRoleSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ...models import InterfaceProfile
from .profile_group import ProfileGroupSerializer


class InterfaceProfileSerializer(NetBoxModelSerializer):
    """Serializer for InterfaceProfile."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_interface_profiles-api:interfaceprofile-detail"
    )
    group = ProfileGroupSerializer(nested=True, required=False, allow_null=True)
    device_roles = DeviceRoleSerializer(many=True, nested=True, required=False)

    class Meta:
        model = InterfaceProfile
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
