"""
Serializer for the interface configuration API endpoint.
"""

from dcim.api.serializers import InterfaceSerializer
from dcim.models import Interface
from drf_spectacular.utils import extend_schema_field
from netbox.api.serializers import BaseModelSerializer
from rest_framework import serializers

from ...services import InterfaceConfig, resolve_interface_config
from .interface_role import InterfaceRoleSerializer
from .interface_role_assignment import InterfaceRoleAssignmentSerializer
from .interface_template import InterfaceTemplateSerializer
from .profile_config_template import ProfileConfigTemplateSerializer


class InterfaceConfigSerializer(BaseModelSerializer):
    """The interface role of an interface, the templates that apply to it and its rendered configuration.

    The object's ID is the ID of the interface.
    """

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:interface_profiles-api:interfaceconfig-detail")
    interface = serializers.SerializerMethodField()
    role_assignment = serializers.SerializerMethodField()
    interface_role = serializers.SerializerMethodField()
    interface_template = serializers.SerializerMethodField()
    config_template = serializers.SerializerMethodField()
    config = serializers.SerializerMethodField()
    config_error = serializers.SerializerMethodField()

    class Meta:
        model = Interface
        fields = (
            "id",
            "url",
            "display",
            "interface",
            "role_assignment",
            "interface_role",
            "interface_template",
            "config_template",
            "config",
            "config_error",
        )
        brief_fields = ("id", "url", "display", "interface_role")

    def _resolve(self, obj) -> InterfaceConfig:
        """Resolve the interface configuration once per object, rendering only when the config is requested."""
        if (resolved := getattr(obj, "_interface_config", None)) is None:
            render = "config" in self.fields or "config_error" in self.fields

            # Interfaces of the same device share its config context, which is computed only once per response
            device_contexts = self.context.setdefault("_device_config_contexts", {})
            device_context = None
            if render:
                device = obj.device
                if device.pk not in device_contexts:
                    device_contexts[device.pk] = device.get_config_context()
                device_context = device_contexts[device.pk]

            resolved = resolve_interface_config(obj, render=render, device_context=device_context)
            obj._interface_config = resolved
        return resolved

    def _nested(self, serializer_class, instance):
        if instance is None:
            return None
        return serializer_class(instance, nested=True, context=self.context).data

    @extend_schema_field(InterfaceSerializer(nested=True))
    def get_interface(self, obj):
        return self._nested(InterfaceSerializer, obj)

    @extend_schema_field(InterfaceRoleAssignmentSerializer(nested=True, allow_null=True))
    def get_role_assignment(self, obj):
        assignment = self._resolve(obj).assignment
        if assignment is None:
            return None
        return InterfaceRoleAssignmentSerializer(
            assignment, nested=True, fields=("id", "url", "display"), context=self.context
        ).data

    @extend_schema_field(InterfaceRoleSerializer(nested=True, allow_null=True))
    def get_interface_role(self, obj):
        return self._nested(InterfaceRoleSerializer, self._resolve(obj).interface_role)

    @extend_schema_field(InterfaceTemplateSerializer(nested=True, allow_null=True))
    def get_interface_template(self, obj):
        return self._nested(InterfaceTemplateSerializer, self._resolve(obj).interface_template)

    @extend_schema_field(ProfileConfigTemplateSerializer(nested=True, allow_null=True))
    def get_config_template(self, obj):
        return self._nested(ProfileConfigTemplateSerializer, self._resolve(obj).config_template)

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_config(self, obj):
        return self._resolve(obj).config

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_config_error(self, obj):
        return self._resolve(obj).config_error
