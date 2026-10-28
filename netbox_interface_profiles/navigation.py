"""
Navigation menu items for netbox interface profiles.

For more information on navigation menus, see:
https://docs.netbox.dev/en/stable/plugins/development/navigation/
"""

from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem


def _menu_item(model_name: str, link_text: str) -> PluginMenuItem:
    """Build a menu item linking to a model's list view, with Add and Import buttons."""
    return PluginMenuItem(
        link=f"plugins:netbox_interface_profiles:{model_name}_list",
        link_text=link_text,
        buttons=(
            PluginMenuButton(
                link=f"plugins:netbox_interface_profiles:{model_name}_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
            ),
            PluginMenuButton(
                link=f"plugins:netbox_interface_profiles:{model_name}_import",
                title="Import",
                icon_class="mdi mdi-upload",
            ),
        ),
        auth_required=True,
    )


# Items follow the model relations: groups contain roles, which are assigned to interfaces
roles = (
    _menu_item("rolegroup", "Role Groups"),
    _menu_item("interfacerole", "Interface Roles"),
    _menu_item("interfaceroleassignment", "Assignments"),
    PluginMenuItem(
        link="plugins:netbox_interface_profiles:rolesync_list",
        link_text="Synchronizations",
        permissions=["netbox_interface_profiles.view_rolesync"],
    ),
)

# Interface templates belong to a role, config templates to an interface template
templates = (
    _menu_item("interfacetemplate", "Interface Templates"),
    _menu_item("profileconfigtemplate", "Config Templates"),
)

menu = PluginMenu(
    label="Interface Roles",
    groups=(
        ("Roles", roles),
        ("Templates", templates),
    ),
    icon_class="mdi mdi-ethernet",
)
