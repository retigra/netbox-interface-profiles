"""
ProfileGroup table for netbox interface profiles.
"""

import django_tables2 as tables
from netbox.tables import OrganizationalModelTable, columns

from ..models import ProfileGroup


class ProfileGroupTable(OrganizationalModelTable):
    name = tables.Column(linkify=True)
    interface_profile_count = columns.LinkedCountColumn(
        viewname="plugins:netbox_interface_profiles:interfaceprofile_list",
        url_params={"group_id": "pk"},
        verbose_name="Profiles",
    )
    tags = columns.TagColumn(url_name="plugins:netbox_interface_profiles:profilegroup_list")

    class Meta(OrganizationalModelTable.Meta):
        model = ProfileGroup
        fields = (
            "pk",
            "id",
            "name",
            "slug",
            "description",
            "interface_profile_count",
            "owner",
            "comments",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "name",
            "description",
            "interface_profile_count",
        )
