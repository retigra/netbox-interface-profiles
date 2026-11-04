"""
InterfaceTemplate serializer for interface profiles API.
"""

from dcim.api.serializers import SiteGroupSerializer, SiteSerializer
from dcim.models import Site, SiteGroup
from django.contrib.contenttypes.models import ContentType
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ...models import InterfaceTemplate
from .interface_role import InterfaceRoleSerializer


class InterfaceTemplateSerializer(NetBoxModelSerializer):
    """Serializer for InterfaceTemplate."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:interface_profiles-api:interfacetemplate-detail")
    interface_role = InterfaceRoleSerializer(nested=True)
    scope_type = ContentTypeField(
        queryset=ContentType.objects.filter(app_label="dcim", model__in=("site", "sitegroup")),
        required=False,
        allow_null=True,
    )
    scope_id = serializers.IntegerField(required=False, allow_null=True)
    scope = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = InterfaceTemplate
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "interface_role",
            "scope_type",
            "scope_id",
            "scope",
            "speed",
            "duplex",
            "mtu",
            "mode",
            "enabled",
            "poe_mode",
            "untagged_vlan_vid",
            "tagged_vlans_vids",
            "set_null_speed",
            "set_null_duplex",
            "set_null_mtu",
            "set_null_mode",
            "set_null_poe_mode",
            "set_null_untagged_vlan_vid",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name")

    def get_scope(self, obj):
        if obj.scope is None:
            return None
        request = self.context.get("request")
        if isinstance(obj.scope, Site):
            return SiteSerializer(obj.scope, nested=True, context={"request": request}).data
        if isinstance(obj.scope, SiteGroup):
            return SiteGroupSerializer(obj.scope, nested=True, context={"request": request}).data
        return str(obj.scope)
