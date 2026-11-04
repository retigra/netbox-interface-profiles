"""
InterfaceTemplate table for interface profiles.
"""

import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from ..models import InterfaceTemplate


class InterfaceTemplateTable(NetBoxTable):
    name = tables.Column(linkify=True)
    interface_role = tables.Column(linkify=True)
    scope = tables.Column(verbose_name="Scope", default="—", orderable=False, linkify=True)
    enabled = columns.BooleanColumn()
    mgmt_only = columns.BooleanColumn(verbose_name="Management only")
    interface_description = tables.Column(verbose_name="Interface description")
    speed = tables.Column(verbose_name="Speed (Kbps)")
    duplex = columns.ChoiceFieldColumn()
    mtu = tables.Column(verbose_name="MTU")
    vrf = tables.Column(linkify=True, verbose_name="VRF")
    mode = columns.ChoiceFieldColumn(verbose_name="802.1Q mode")
    untagged_vlan_vid = tables.Column(verbose_name="Untagged VLAN VID")
    tagged_vlans_vids = tables.TemplateColumn(
        template_code='{{ value|join:", " }}',
        verbose_name="Tagged VLAN VIDs",
        orderable=False,
    )
    qinq_svlan_vid = tables.Column(verbose_name="Q-in-Q SVLAN VID")
    vlan_translation_policy = tables.Column(linkify=True, verbose_name="VLAN translation policy")
    poe_mode = columns.ChoiceFieldColumn(verbose_name="PoE mode")
    poe_type = columns.ChoiceFieldColumn(verbose_name="PoE type")
    set_null_interface_description = columns.BooleanColumn(verbose_name="Clear interface description")
    set_null_speed = columns.BooleanColumn(verbose_name="Clear speed")
    set_null_duplex = columns.BooleanColumn(verbose_name="Clear duplex")
    set_null_mtu = columns.BooleanColumn(verbose_name="Clear MTU")
    set_null_vrf = columns.BooleanColumn(verbose_name="Clear VRF")
    set_null_mode = columns.BooleanColumn(verbose_name="Clear mode")
    set_null_untagged_vlan_vid = columns.BooleanColumn(verbose_name="Clear untagged VLAN")
    set_null_qinq_svlan_vid = columns.BooleanColumn(verbose_name="Clear Q-in-Q SVLAN")
    set_null_vlan_translation_policy = columns.BooleanColumn(verbose_name="Clear VLAN translation policy")
    set_null_poe_mode = columns.BooleanColumn(verbose_name="Clear PoE mode")
    set_null_poe_type = columns.BooleanColumn(verbose_name="Clear PoE type")
    tags = columns.TagColumn(url_name="plugins:interface_profiles:interfacetemplate_list")

    class Meta(NetBoxTable.Meta):
        model = InterfaceTemplate
        fields = (
            "pk",
            "id",
            "name",
            "interface_role",
            "scope",
            "description",
            "enabled",
            "mgmt_only",
            "interface_description",
            "speed",
            "duplex",
            "mtu",
            "vrf",
            "mode",
            "untagged_vlan_vid",
            "tagged_vlans_vids",
            "qinq_svlan_vid",
            "vlan_translation_policy",
            "poe_mode",
            "poe_type",
            "set_null_interface_description",
            "set_null_speed",
            "set_null_duplex",
            "set_null_mtu",
            "set_null_vrf",
            "set_null_mode",
            "set_null_untagged_vlan_vid",
            "set_null_qinq_svlan_vid",
            "set_null_vlan_translation_policy",
            "set_null_poe_mode",
            "set_null_poe_type",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "name",
            "interface_role",
            "scope",
            "mode",
            "untagged_vlan_vid",
            "tagged_vlans_vids",
            "enabled",
        )
