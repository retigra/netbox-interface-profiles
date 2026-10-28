"""
InterfaceProfile table for netbox interface profiles.
"""

import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from ..models import InterfaceProfile


class InterfaceProfileTable(NetBoxTable):
    name = tables.Column(linkify=True)
    group = tables.Column(linkify=True)
    description = tables.Column()
    device_roles = columns.ManyToManyColumn(linkify_item=True)
    tags = columns.TagColumn(url_name="plugins:netbox_interface_profiles:interfaceprofile_list")

    class Meta(NetBoxTable.Meta):
        model = InterfaceProfile
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
