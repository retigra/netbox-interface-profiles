"""
InterfaceTemplate serializer for netbox interface profiles API.
"""

from dcim.api.serializers import SiteGroupSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ...models import InterfaceTemplate
from .interface_profile import InterfaceProfileSerializer


class InterfaceTemplateSerializer(NetBoxModelSerializer):
    """Serializer for InterfaceTemplate."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_interface_profiles-api:interfacetemplate-detail"
    )
    interface_profile = InterfaceProfileSerializer(nested=True)
    site_group = SiteGroupSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = InterfaceTemplate
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "interface_profile",
            "site_group",
            "speed",
            "duplex",
            "mtu",
            "mode",
            "enabled",
            "poe_mode",
            "untagged_vlan_vid",
            "tagged_vlans_vids",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name")
