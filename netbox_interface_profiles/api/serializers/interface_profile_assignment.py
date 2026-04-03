"""
InterfaceProfileAssignment serializer for netbox interface profiles API.
"""

from dcim.api.serializers import InterfaceSerializer
from dcim.models import Interface
from netbox.api.fields import SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ...models import InterfaceProfile, InterfaceProfileAssignment
from .interface_profile import InterfaceProfileSerializer


class InterfaceProfileAssignmentSerializer(NetBoxModelSerializer):
    """Serializer for InterfaceProfileAssignment."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_interface_profiles-api:interfaceprofileassignment-detail"
    )
    interface = SerializedPKRelatedField(
        queryset=Interface.objects.all(),
        serializer=InterfaceSerializer,
        nested=True,
    )
    interface_profile = SerializedPKRelatedField(
        queryset=InterfaceProfile.objects.all(),
        serializer=InterfaceProfileSerializer,
        nested=True,
    )

    class Meta:
        model = InterfaceProfileAssignment
        fields = (
            "id",
            "url",
            "display",
            "interface",
            "interface_profile",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "interface", "interface_profile")
