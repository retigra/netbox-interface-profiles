"""
InterfaceProfile table for netbox interface profiles.
"""

import django_tables2 as tables
from netbox.tables import NetBoxTable

from ..models import InterfaceProfile


class InterfaceProfileTable(NetBoxTable):
    name = tables.Column(linkify=True)
    description = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = InterfaceProfile
        fields = (
            "id",
            "name",
            "description",
        )
        default_columns = (
            "name",
            "description",
        )
