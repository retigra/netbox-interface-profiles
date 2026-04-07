"""
ProfileConfigTemplate serializer for netbox interface profiles API.
"""

from dcim.api.serializers import DeviceTypeSerializer, PlatformSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ...models import ProfileConfigTemplate
from .interface_profile import InterfaceProfileSerializer


class ProfileConfigTemplateSerializer(NetBoxModelSerializer):
    """Serializer for ProfileConfigTemplate."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_interface_profiles-api:profileconfigtemplate-detail"
    )
    interface_profile = InterfaceProfileSerializer(
        nested=True,
    )
    platform = PlatformSerializer(
        nested=True,
    )
    device_type = DeviceTypeSerializer(
        nested=True,
    )

    class Meta:
        model = ProfileConfigTemplate
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "interface_profile",
            "platform",
            "device_type",
            "template_code",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "name",
            "interface_profile",
            "platform",
            "device_type",
        )
