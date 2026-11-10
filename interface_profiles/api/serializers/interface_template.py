"""
InterfaceTemplate serializer for interface profiles API.
"""

from dcim.choices import InterfaceDuplexChoices, InterfaceModeChoices, InterfacePoEModeChoices, InterfacePoETypeChoices
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from ipam.api.serializers import VLANTranslationPolicySerializer, VRFSerializer
from ipam.constants import VLAN_VID_MAX, VLAN_VID_MIN
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from utilities.api import get_serializer_for_model

from ...models import InterfaceTemplate
from ...models.interface_template import SCOPE_RELATIONS
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
    scope_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        help_text="IDs of the sites or site groups in scope, depending on the scope type.",
    )
    scopes = serializers.SerializerMethodField(read_only=True)
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
            "scope_ids",
            "scopes",
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
        if not self.nested:
            self._validate_scope(data)
        return super().validate(data)

    def _validate_scope(self, data):
        """Replace scope_ids by the scope relation of the scope type, which is validated and saved as M2M field."""
        scope_ids = data.pop("scope_ids", None)
        scope_type = data["scope_type"] if "scope_type" in data else getattr(self.instance, "scope_type", None)
        if scope_ids is None:
            # Changing the scope type of an existing template needs new objects in scope
            if "scope_type" not in data or self.instance is None or scope_type == self.instance.scope_type:
                return
            scope_ids = []
        if scope_ids and scope_type is None:
            raise serializers.ValidationError({"scope_type": "Please select a scope type."})

        scopes = []
        if scope_type is not None:
            scopes = list(scope_type.model_class().objects.filter(pk__in=scope_ids))
            if missing := sorted(set(scope_ids) - {scope.pk for scope in scopes}):
                raise serializers.ValidationError(
                    {
                        "scope_ids": "Related objects not found using the provided values: "
                        f"{', '.join(map(str, missing))}."
                    }
                )
        selected = SCOPE_RELATIONS.get(scope_type.model) if scope_type else None
        for relation in SCOPE_RELATIONS.values():
            data[relation] = scopes if relation == selected else []

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_scopes(self, obj):
        scopes = obj.scope_objects
        if scopes is None:
            return []
        # Serialized like NetBox's GFKSerializerField, for multiple objects
        serializer = get_serializer_for_model(scopes.model)
        return serializer(scopes, many=True, nested=True, context={"request": self.context.get("request")}).data


# NetBox resolves the serializer of a model as <ModelName>Serializer, e.g. for event rules and change logging
InterfaceTemplateSerializer = InterfaceRoleTemplateSerializer
