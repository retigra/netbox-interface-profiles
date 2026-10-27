"""
ProfileConfigTemplate table for netbox interface profiles.
"""

import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from ..models import ProfileConfigTemplate


class ProfileConfigTemplateTable(NetBoxTable):
    """Table for listing ProfileConfigTemplate objects."""

    name = tables.Column(linkify=True)
    interface_template = tables.Column(linkify=True)
    platform = tables.Column(linkify=True)
    device_type = tables.Column(linkify=True)
    description = tables.Column()
    tags = columns.TagColumn(url_name="plugins:netbox_interface_profiles:profileconfigtemplate_list")

    class Meta(NetBoxTable.Meta):
        model = ProfileConfigTemplate
        fields = (
            "pk",
            "id",
            "name",
            "interface_template",
            "platform",
            "device_type",
            "description",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "name",
            "interface_template",
            "platform",
            "device_type",
            "description",
        )
