"""
InterfaceTemplate table for netbox interface profiles.
"""

import django_tables2 as tables
from netbox.tables import NetBoxTable

from ..models import InterfaceTemplate


class InterfaceTemplateTable(NetBoxTable):
    name = tables.Column(linkify=True)
    interface_profile = tables.Column(linkify=True)
    site_group = tables.Column(linkify=True, default="—")
    speed = tables.Column(verbose_name="Speed (Mbps)")
    mode = tables.Column()
    enabled = tables.BooleanColumn()

    class Meta(NetBoxTable.Meta):
        model = InterfaceTemplate
        fields = (
            "id",
            "pk",
            "name",
            "interface_profile",
            "site_group",
            "speed",
            "mode",
            "enabled",
        )
        default_columns = (
            "name",
            "interface_profile",
            "site_group",
            "speed",
            "mode",
            "enabled",
        )
