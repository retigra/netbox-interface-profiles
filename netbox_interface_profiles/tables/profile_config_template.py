"""
ProfileConfigTemplate table for netbox interface profiles.
"""

import django_tables2 as tables
from netbox.tables import NetBoxTable

from ..models import ProfileConfigTemplate


class ProfileConfigTemplateTable(NetBoxTable):
    """Table for listing ProfileConfigTemplate objects."""

    name = tables.Column(linkify=True)
    interface_profile = tables.Column(linkify=True)
    platform = tables.Column(linkify=True)
    device_type = tables.Column(linkify=True)
    description = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = ProfileConfigTemplate
        fields = (
            "pk",
            "id",
            "name",
            "interface_profile",
            "platform",
            "device_type",
            "description",
            "actions",
        )
        default_columns = (
            "name",
            "interface_profile",
            "platform",
            "device_type",
            "description",
        )
