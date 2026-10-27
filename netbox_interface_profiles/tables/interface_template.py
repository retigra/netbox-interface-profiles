"""
InterfaceTemplate table for netbox interface profiles.
"""

import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from ..models import InterfaceTemplate


class InterfaceTemplateTable(NetBoxTable):
    name = tables.Column(linkify=True)
    interface_profile = tables.Column(linkify=True)
    scope = tables.Column(verbose_name="Scope", default="—", orderable=False)
    speed = tables.Column(verbose_name="Speed (Mbps)")
    mode = tables.Column()
    enabled = tables.BooleanColumn()
    mtu = tables.Column(verbose_name="MTU")
    poe_mode = tables.Column(verbose_name="PoE Mode")
    untagged_vlan_vid = tables.Column(verbose_name="Untagged VLAN VID")
    tagged_vlans_vids = tables.TemplateColumn(
        template_code='{{ value|join:", " }}',
        verbose_name="Tagged VLAN VIDs",
        orderable=False,
    )
    tags = columns.TagColumn(url_name="plugins:netbox_interface_profiles:interfacetemplate_list")

    class Meta(NetBoxTable.Meta):
        model = InterfaceTemplate
        fields = (
            "pk",
            "id",
            "name",
            "interface_profile",
            "scope",
            "description",
            "speed",
            "duplex",
            "mtu",
            "mode",
            "enabled",
            "poe_mode",
            "untagged_vlan_vid",
            "tagged_vlans_vids",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "name",
            "interface_profile",
            "scope",
            "speed",
            "mode",
            "enabled",
        )
