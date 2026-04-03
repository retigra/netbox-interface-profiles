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

profile_config_template_buttons = [
    PluginMenuButton(
        link="plugins:netbox_interface_profiles:profileconfigtemplate_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    ),
    PluginMenuButton(
        link="plugins:netbox_interface_profiles:profileconfigtemplate_import",
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

profile_config_templates = (
    PluginMenuItem(
        link="plugins:netbox_interface_profiles:profileconfigtemplate_list",
        link_text="Config Templates",
        buttons=profile_config_template_buttons,
        auth_required=True,
    ),
)

assignment_buttons = [
    PluginMenuButton(
        link="plugins:netbox_interface_profiles:interfaceprofileassignment_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    ),
    PluginMenuButton(
        link="plugins:netbox_interface_profiles:interfaceprofileassignment_import",
        title="Import",
        icon_class="mdi mdi-upload",
    ),
]

assignments = (
    PluginMenuItem(
        link="plugins:netbox_interface_profiles:interfaceprofileassignment_list",
        link_text="Assignments",
        buttons=assignment_buttons,
        auth_required=True,
    ),
)

menu = PluginMenu(
    label="Interface Profiles",
    groups=(
        ("Profiles", interface_profiles),
        ("Templates", profile_config_templates),
        ("Assignments", assignments),
    ),
    icon_class="mdi mdi-ethernet",
)
