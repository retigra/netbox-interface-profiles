"""
InterfaceProfileAssignment serializer for netbox interface profiles API.
"""

from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ...models import InterfaceProfileAssignment


class InterfaceProfileAssignmentSerializer(NetBoxModelSerializer):
    """Serializer for InterfaceProfileAssignment."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_interface_profiles-api:interfaceprofileassignment-detail"
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
