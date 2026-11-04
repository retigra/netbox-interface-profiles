"""
ProfileConfigTemplate table for interface profiles.
"""

import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from ..models import ProfileConfigTemplate


class ScopeTagColumn(columns.TagColumn):
    """Tags limiting the scope of a template, shown without links as tag links filter on the template's own tags."""

    def __init__(self, verbose_name: str):
        super().__init__()
        self.verbose_name = verbose_name


class ProfileConfigTemplateTable(NetBoxTable):
    """Table for listing ProfileConfigTemplate objects."""

    name = tables.Column(linkify=True)
    interface_role = tables.Column(linkify=True)
    platform = tables.Column(linkify=True)
    device_type = tables.Column(linkify=True)
    device_tags = ScopeTagColumn(verbose_name="Device Tags")
    interface_tags = ScopeTagColumn(verbose_name="Interface Tags")
    weight = tables.Column()
    description = tables.Column()
    data_source = tables.Column(linkify=True)
    data_file = tables.Column(linkify=True)
    is_synced = columns.BooleanColumn(orderable=False, verbose_name="Synced")
    auto_sync_enabled = columns.BooleanColumn(orderable=False, verbose_name="Auto Sync Enabled")
    debug = columns.BooleanColumn(false_mark=None)
    tags = columns.TagColumn(url_name="plugins:interface_profiles:profileconfigtemplate_list")

    class Meta(NetBoxTable.Meta):
        model = ProfileConfigTemplate
        fields = (
            "pk",
            "id",
            "name",
            "interface_role",
            "platform",
            "device_type",
            "device_tags",
            "interface_tags",
            "weight",
            "description",
            "data_source",
            "data_file",
            "data_synced",
            "is_synced",
            "auto_sync_enabled",
            "debug",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "name",
            "interface_role",
            "platform",
            "device_type",
            "device_tags",
            "interface_tags",
            "weight",
            "is_synced",
        )
