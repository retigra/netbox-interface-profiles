"""
InterfaceTemplate serializer for interface profiles API.
"""

from dcim.api.serializers import SiteGroupSerializer, SiteSerializer
from dcim.choices import InterfaceDuplexChoices, InterfaceModeChoices, InterfacePoEModeChoices, InterfacePoETypeChoices
from dcim.models import Site, SiteGroup
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from ipam.api.serializers import VLANTranslationPolicySerializer, VRFSerializer
from ipam.constants import VLAN_VID_MAX, VLAN_VID_MIN
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ...models import InterfaceTemplate
from .interface_role import InterfaceRoleSerializer


class InterfaceRoleTemplateSerializer(NetBoxModelSerializer):
    """Serializer for InterfaceTemplate.

    The class is named after the GraphQL type, as an "InterfaceTemplate" OpenAPI component would collide with
    NetBox's own dcim interface templates. NetBox looks the serializer up by model name, see the alias below.
    """

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:interface_profiles-api:interfacetemplate-detail")
    interface_role = InterfaceRoleSerializer(nested=True)
    scope_type = ContentTypeField(
        queryset=ContentType.objects.filter(app_label="dcim", model__in=("site", "sitegroup")),
        required=False,
        allow_null=True,
    )
    scope_id = serializers.IntegerField(required=False, allow_null=True)
    scope = serializers.SerializerMethodField(read_only=True)
    duplex = ChoiceField(choices=InterfaceDuplexChoices, required=False, allow_blank=True, allow_null=True)
    mode = ChoiceField(choices=InterfaceModeChoices, required=False, allow_blank=True, allow_null=True)
    poe_mode = ChoiceField(choices=InterfacePoEModeChoices, required=False, allow_blank=True, allow_null=True)
    poe_type = ChoiceField(choices=InterfacePoETypeChoices, required=False, allow_blank=True, allow_null=True)
    vrf = VRFSerializer(nested=True, required=False, allow_null=True)
    vlan_translation_policy = VLANTranslationPolicySerializer(nested=True, required=False, allow_null=True)
    tagged_vlans_vids = serializers.ListField(
        child=serializers.IntegerField(min_value=VLAN_VID_MIN, max_value=VLAN_VID_MAX),
        required=False,
        help_text="VIDs of the tagged VLANs, resolved to the VLANs with these VIDs in the site of the interface.",
    )

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
            "enabled",
            "mgmt_only",
            "interface_description",
            "speed",
            "duplex",
            "mtu",
            "vrf",
            "mode",
            "untagged_vlan_vid",
            "tagged_vlans_vids",
            "qinq_svlan_vid",
            "vlan_translation_policy",
            "poe_mode",
            "poe_type",
            "set_null_interface_description",
            "set_null_speed",
            "set_null_duplex",
            "set_null_mtu",
            "set_null_vrf",
            "set_null_mode",
            "set_null_untagged_vlan_vid",
            "set_null_qinq_svlan_vid",
            "set_null_vlan_translation_policy",
            "set_null_poe_mode",
            "set_null_poe_type",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "description")

    def validate(self, data):
        # Store blank choices as null, like the forms do
        for field in ("duplex", "mode", "poe_mode", "poe_type"):
            if data.get(field) == "":
                data[field] = None
        return super().validate(data)

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_scope(self, obj):
        if obj.scope is None:
            return None
        request = self.context.get("request")
        if isinstance(obj.scope, Site):
            return SiteSerializer(obj.scope, nested=True, context={"request": request}).data
        if isinstance(obj.scope, SiteGroup):
            return SiteGroupSerializer(obj.scope, nested=True, context={"request": request}).data
        return str(obj.scope)


# NetBox resolves the serializer of a model as <ModelName>Serializer, e.g. for event rules and change logging
InterfaceTemplateSerializer = InterfaceRoleTemplateSerializer
