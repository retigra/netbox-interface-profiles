"""
RoleGroup serializer for netbox interface profiles API.
"""

from netbox.api.fields import RelatedObjectCountField
from netbox.api.serializers import OrganizationalModelSerializer
from rest_framework import serializers

from ...models import RoleGroup


class RoleGroupSerializer(OrganizationalModelSerializer):
    """Serializer for RoleGroup."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_interface_profiles-api:rolegroup-detail")
    interface_role_count = RelatedObjectCountField("interface_roles")

    class Meta:
        model = RoleGroup
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
            "interface_role_count",
        )
        brief_fields = ("id", "url", "display", "name", "slug", "description")
