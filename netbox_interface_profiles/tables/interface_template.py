"""
InterfaceTemplate table for netbox interface profiles.
"""

import django_tables2 as tables
from netbox.tables import NetBoxTable

from ..models import InterfaceTemplate


class InterfaceTemplateTable(NetBoxTable):
    name = tables.Column(linkify=True)
    interface_profile = tables.Column(linkify=True)
    scope = tables.Column(verbose_name="Scope", default="—", orderable=False)
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
            "scope",
            "speed",
            "mode",
            "enabled",
        )
        default_columns = (
            "name",
            "interface_profile",
            "scope",
            "speed",
            "mode",
            "enabled",
        )
