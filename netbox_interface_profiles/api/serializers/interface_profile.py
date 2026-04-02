"""
InterfaceProfile serializer for netbox interface profiles API.
"""

from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ...models import InterfaceProfile


class InterfaceProfileSerializer(NetBoxModelSerializer):
    """Serializer for InterfaceProfile."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_interface_profiles-api:interfaceprofile-detail"
    )

    class Meta:
        model = InterfaceProfile
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "description")
