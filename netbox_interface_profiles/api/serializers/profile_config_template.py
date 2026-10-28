"""
ProfileConfigTemplate serializer for netbox interface profiles API.
"""

from core.api.serializers import DataFileSerializer, DataSourceSerializer
from dcim.api.serializers import DeviceTypeSerializer, PlatformSerializer
from extras.api.serializers import TagSerializer
from extras.models import Tag
from netbox.api.fields import SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ...models import ProfileConfigTemplate
from .interface_role import InterfaceRoleSerializer


class ProfileConfigTemplateSerializer(NetBoxModelSerializer):
    """Serializer for ProfileConfigTemplate."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_interface_profiles-api:profileconfigtemplate-detail"
    )
    interface_role = InterfaceRoleSerializer(nested=True)
    platform = PlatformSerializer(nested=True)
    device_type = DeviceTypeSerializer(nested=True, required=False, allow_null=True)
    device_tags = SerializedPKRelatedField(
        queryset=Tag.objects.all(),
        serializer=TagSerializer,
        nested=True,
        required=False,
        many=True,
    )
    interface_tags = SerializedPKRelatedField(
        queryset=Tag.objects.all(),
        serializer=TagSerializer,
        nested=True,
        required=False,
        many=True,
    )
    data_source = DataSourceSerializer(nested=True, required=False)
    data_file = DataFileSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ProfileConfigTemplate
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "interface_role",
            "platform",
            "device_type",
            "device_tags",
            "interface_tags",
            "weight",
            "template_code",
            "environment_params",
            "debug",
            "data_source",
            "data_path",
            "data_file",
            "auto_sync_enabled",
            "data_synced",
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
            "interface_role",
            "platform",
            "device_type",
            "weight",
        )
        model_clean_fields = ("data_source", "data_path", "auto_sync_enabled", "data_synced", "template_code")
