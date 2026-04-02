"""
Navigation menu items for netbox interface profiles.

For more information on navigation menus, see:
https://docs.netbox.dev/en/stable/plugins/development/navigation/
"""

from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

interface_profile_buttons = [
    PluginMenuButton(
        link="plugins:netbox_interface_profiles:interfaceprofile_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    ),
    PluginMenuButton(
        link="plugins:netbox_interface_profiles:interfaceprofile_import",
        title="Import",
        icon_class="mdi mdi-upload",
    ),
]

interface_profiles = (
    PluginMenuItem(
        link="plugins:netbox_interface_profiles:interfaceprofile_list",
        link_text="Interface Profiles",
        buttons=interface_profile_buttons,
        auth_required=True,
    ),
)

menu = PluginMenu(
    label="Interface Profiles",
    groups=(("Profiles", interface_profiles),),
    icon_class="mdi mdi-ethernet",
)
