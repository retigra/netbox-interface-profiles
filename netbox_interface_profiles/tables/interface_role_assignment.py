"""
Tables for InterfaceRoleAssignment and the Device interface tab.
"""

import django_tables2 as tables
from dcim.models import Interface
from dcim.tables import DeviceInterfaceTable as CoreDeviceInterfaceTable
from dcim.tables.template_code import INTERFACE_BUTTONS
from netbox.tables import NetBoxTable, columns

from ..models import InterfaceRoleAssignment

INTERFACE_ROLE_BUTTONS = """
<span class="dropdown">
        <button
            type="button"
            class="btn btn-cyan btn-sm dropdown-toggle"
            data-bs-toggle="dropdown"
            aria-haspopup="true"
            aria-expanded="false"
            title="Assign Interface Role"
            hx-get="{% url 'plugins:netbox_interface_profiles:interfaceroleassignment_htmx_menu' interface_id=record.pk %}"
            hx-target="#interface-role-menu-{{ record.pk }}"
            hx-swap="innerHTML"
        >
      <span class="mdi mdi-account" aria-hidden="true"></span>
    </button>
        <ul id="interface-role-menu-{{ record.pk }}" class="dropdown-menu dropdown-menu-end">
            <li><span class="dropdown-item-text text-muted">Loading roles...</span></li>
        </ul>
</span>
"""

# NetBox's interface row buttons hardcode the legacy interfaces tab as return URL; point them back to this tab
DEVICE_INTERFACE_BUTTONS = INTERFACE_BUTTONS.replace(
    "{% url 'dcim:device_interfaces' pk=object.pk %}",
    "{% url 'dcim:device_interface_roles' pk=object.pk %}",
)


class InterfaceRoleAssignmentTable(NetBoxTable):
    """Table for listing InterfaceRoleAssignment objects in CRUD views."""

    interface = tables.Column(linkify=True)
    device = tables.Column(
        accessor="interface.device",
        verbose_name="Device",
        linkify=True,
        orderable=False,
    )
    interface_role = tables.Column(linkify=True)
    interface_role_group = tables.Column(
        accessor="interface_role.group",
        verbose_name="Role Group",
        linkify=True,
        order_by=("interface_role__group__name",),
    )
    tags = columns.TagColumn(url_name="plugins:netbox_interface_profiles:interfaceroleassignment_list")

    class Meta(NetBoxTable.Meta):
        model = InterfaceRoleAssignment
        fields = (
            "pk",
            "id",
            "interface",
            "device",
            "interface_role",
            "interface_role_group",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "interface",
            "device",
            "interface_role",
        )


class DeviceInterfaceTable(CoreDeviceInterfaceTable):
    """
    Device interface table for the Device 'Interface Roles' tab.

    Extends the standard NetBox device interface table with the assigned
    interface role.
    """

    interface_role = tables.Column(
        accessor="role_assignment.interface_role",
        verbose_name="Interface Role",
        linkify=True,
        default="—",
    )

    actions = columns.ActionsColumn(extra_buttons=INTERFACE_ROLE_BUTTONS + DEVICE_INTERFACE_BUTTONS)

    class Meta(CoreDeviceInterfaceTable.Meta):
        model = Interface
        fields = CoreDeviceInterfaceTable.Meta.fields + ("interface_role",)
        default_columns = CoreDeviceInterfaceTable.Meta.default_columns + ("interface_role",)
