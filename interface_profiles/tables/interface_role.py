"""
InterfaceRole table for interface profiles.
"""

import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from ..models import InterfaceRole


class InterfaceRoleTable(NetBoxTable):
    name = tables.Column(linkify=True)
    group = tables.Column(linkify=True)
    description = tables.Column()
    device_roles = columns.ManyToManyColumn(linkify_item=True)
    tags = columns.TagColumn(url_name="plugins:interface_profiles:interfacerole_list")

    class Meta(NetBoxTable.Meta):
        model = InterfaceRole
        fields = (
            "pk",
            "id",
            "name",
            "group",
            "description",
            "device_roles",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "name",
            "group",
            "description",
        )
