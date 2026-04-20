"""
ProfileConfigTemplate serializer for netbox interface profiles API.
"""

from dcim.api.serializers import DeviceTypeSerializer, PlatformSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ...models import ProfileConfigTemplate
from .interface_template import InterfaceTemplateSerializer


class ProfileConfigTemplateSerializer(NetBoxModelSerializer):
    """Serializer for ProfileConfigTemplate."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_interface_profiles-api:profileconfigtemplate-detail"
    )
    interface_template = InterfaceTemplateSerializer(nested=True)
    platform = PlatformSerializer(nested=True)
    device_type = DeviceTypeSerializer(nested=True)

    class Meta:
        model = ProfileConfigTemplate
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "interface_template",
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
            "interface_template",
            "platform",
            "device_type",
        )
