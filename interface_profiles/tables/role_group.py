"""
RoleGroup table for interface profiles.
"""

import django_tables2 as tables
from netbox.tables import OrganizationalModelTable, columns

from ..models import RoleGroup


class RoleGroupTable(OrganizationalModelTable):
    name = tables.Column(linkify=True)
    interface_role_count = columns.LinkedCountColumn(
        viewname="plugins:interface_profiles:interfacerole_list",
        url_params={"group_id": "pk"},
        verbose_name="Roles",
    )
    tags = columns.TagColumn(url_name="plugins:interface_profiles:rolegroup_list")

    class Meta(OrganizationalModelTable.Meta):
        model = RoleGroup
        fields = (
            "pk",
            "id",
            "name",
            "slug",
            "description",
            "interface_role_count",
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
            "interface_role_count",
        )
