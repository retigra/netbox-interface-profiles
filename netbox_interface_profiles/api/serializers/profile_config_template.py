"""
ProfileConfigTemplate serializer for netbox interface profiles API.
"""

from dcim.api.serializers import DeviceTypeSerializer, PlatformSerializer
from dcim.models import DeviceType, Platform
from netbox.api.fields import SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ...models import InterfaceProfile, ProfileConfigTemplate
from .interface_profile import InterfaceProfileSerializer


class ProfileConfigTemplateSerializer(NetBoxModelSerializer):
    """Serializer for ProfileConfigTemplate."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_interface_profiles-api:profileconfigtemplate-detail"
    )
    interface_profile = SerializedPKRelatedField(
        queryset=InterfaceProfile.objects.all(),
        serializer=InterfaceProfileSerializer,
        nested=True,
    )
    platform = SerializedPKRelatedField(
        queryset=Platform.objects.all(),
        serializer=PlatformSerializer,
        nested=True,
    )
    device_type = SerializedPKRelatedField(
        queryset=DeviceType.objects.all(),
        serializer=DeviceTypeSerializer,
        nested=True,
        allow_null=True,
        required=False,
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
