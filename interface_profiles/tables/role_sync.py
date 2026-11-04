"""
RoleSync table for interface profiles.
"""

import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from ..models import RoleSync

MODE_TEMPLATE = """
{% if record.dry_run %}
  <span class="badge text-bg-blue">Dry run</span>
{% else %}
  <span class="badge text-bg-orange">Commit</span>
{% endif %}
"""

STATUS_TEMPLATE = """
{% load helpers %}
{% badge record.get_status_display bg_color=record.get_status_color %}
"""


class RoleSyncTable(NetBoxTable):
    created = columns.DateTimeColumn(linkify=True, verbose_name="Created")
    interface_role = tables.Column(linkify=True, verbose_name="Role")
    mode = tables.TemplateColumn(template_code=MODE_TEMPLATE, accessor="dry_run", verbose_name="Mode")
    status = tables.TemplateColumn(template_code=STATUS_TEMPLATE, accessor="job__status", verbose_name="Status")
    interface_count = tables.Column(verbose_name="Interfaces")
    change_count = tables.Column(verbose_name="Changed Interfaces")
    user = tables.Column(accessor="job__user", verbose_name="User")
    actions = columns.ActionsColumn(actions=("delete",))

    class Meta(NetBoxTable.Meta):
        model = RoleSync
        fields = (
            "pk",
            "id",
            "created",
            "interface_role",
            "mode",
            "status",
            "interface_count",
            "change_count",
            "user",
            "actions",
        )
        default_columns = (
            "created",
            "interface_role",
            "mode",
            "status",
            "interface_count",
            "change_count",
            "user",
        )
