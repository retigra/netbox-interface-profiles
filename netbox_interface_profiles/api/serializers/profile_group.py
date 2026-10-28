"""
ProfileGroup serializer for netbox interface profiles API.
"""

from netbox.api.fields import RelatedObjectCountField
from netbox.api.serializers import OrganizationalModelSerializer
from rest_framework import serializers

from ...models import ProfileGroup


class ProfileGroupSerializer(OrganizationalModelSerializer):
    """Serializer for ProfileGroup."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_interface_profiles-api:profilegroup-detail"
    )
    interface_profile_count = RelatedObjectCountField("interface_profiles")

    class Meta:
        model = ProfileGroup
        fields = (
            "id",
            "url",
            "display",
            "name",
            "slug",
            "description",
            "owner",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
            "interface_profile_count",
        )
        brief_fields = ("id", "url", "display", "name", "slug", "description")
