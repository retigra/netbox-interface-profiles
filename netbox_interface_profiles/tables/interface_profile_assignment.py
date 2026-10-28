"""
Tables for InterfaceProfileAssignment and the Device interface tab.
"""

import django_tables2 as tables
from dcim.models import Interface
from dcim.tables import DeviceInterfaceTable as CoreDeviceInterfaceTable
from dcim.tables.template_code import INTERFACE_BUTTONS
from netbox.tables import NetBoxTable, columns

from ..models import InterfaceProfileAssignment

INTERFACE_PROFILE_BUTTONS = """
<span class="dropdown">
        <button
            type="button"
            class="btn btn-cyan btn-sm dropdown-toggle"
            data-bs-toggle="dropdown"
            aria-haspopup="true"
            aria-expanded="false"
            title="Assign Interface Profile"
            hx-get="{% url 'plugins:netbox_interface_profiles:interfaceprofileassignment_htmx_menu' interface_id=record.pk %}"
            hx-target="#interface-profile-menu-{{ record.pk }}"
            hx-swap="innerHTML"
        >
      <span class="mdi mdi-account" aria-hidden="true"></span>
    </button>
        <ul id="interface-profile-menu-{{ record.pk }}" class="dropdown-menu dropdown-menu-end">
            <li><span class="dropdown-item-text text-muted">Loading profiles...</span></li>
        </ul>
</span>
"""

# NetBox's interface row buttons hardcode the legacy interfaces tab as return URL; point them back to this tab
DEVICE_INTERFACE_BUTTONS = INTERFACE_BUTTONS.replace(
    "{% url 'dcim:device_interfaces' pk=object.pk %}",
    "{% url 'dcim:device_interface_profiles' pk=object.pk %}",
)


class InterfaceProfileAssignmentTable(NetBoxTable):
    """Table for listing InterfaceProfileAssignment objects in CRUD views."""

    interface = tables.Column(linkify=True)
    device = tables.Column(
        accessor="interface.device",
        verbose_name="Device",
        linkify=True,
        orderable=False,
    )
    interface_profile = tables.Column(linkify=True)
    interface_profile_group = tables.Column(
        accessor="interface_profile.group",
        verbose_name="Profile Group",
        linkify=True,
        order_by=("interface_profile__group__name",),
    )
    tags = columns.TagColumn(url_name="plugins:netbox_interface_profiles:interfaceprofileassignment_list")

    class Meta(NetBoxTable.Meta):
        model = InterfaceProfileAssignment
        fields = (
            "pk",
            "id",
            "interface",
            "device",
            "interface_profile",
            "interface_profile_group",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "interface",
            "device",
            "interface_profile",
        )


class DeviceInterfaceTable(CoreDeviceInterfaceTable):
    """
    Device interface table for the Device 'Interface Profiles' tab.

    Extends the standard NetBox device interface table with the assigned
    interface profile.
    """

    interface_profile = tables.Column(
        accessor="profile_assignment.interface_profile",
        verbose_name="Interface Profile",
        linkify=True,
        default="—",
    )

    actions = columns.ActionsColumn(extra_buttons=INTERFACE_PROFILE_BUTTONS + DEVICE_INTERFACE_BUTTONS)

    class Meta(CoreDeviceInterfaceTable.Meta):
        model = Interface
        fields = CoreDeviceInterfaceTable.Meta.fields + ("interface_profile",)
        default_columns = CoreDeviceInterfaceTable.Meta.default_columns + ("interface_profile",)
