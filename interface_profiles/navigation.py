"""
Navigation menu items for interface profiles.

For more information on navigation menus, see:
https://docs.netbox.dev/en/stable/plugins/development/navigation/
"""

from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

APP_LABEL = "interface_profiles"


def _menu_item(model_name: str, link_text: str) -> PluginMenuItem:
    """
    Build a menu item linking to a model's list view, with Add and Import buttons.

    Mirrors NetBox's own `get_model_item()`: the item requires view permission and both buttons add permission,
    so NetBox hides what the user may not use, and the whole menu when nothing is left.
    """
    return PluginMenuItem(
        link=f"plugins:{APP_LABEL}:{model_name}_list",
        link_text=link_text,
        permissions=[f"{APP_LABEL}.view_{model_name}"],
        buttons=(
            PluginMenuButton(
                link=f"plugins:{APP_LABEL}:{model_name}_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=[f"{APP_LABEL}.add_{model_name}"],
            ),
            PluginMenuButton(
                link=f"plugins:{APP_LABEL}:{model_name}_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=[f"{APP_LABEL}.add_{model_name}"],
            ),
        ),
    )


# Items follow the model relations: groups contain roles, which are assigned to interfaces
roles = (
    _menu_item("rolegroup", "Role Groups"),
    _menu_item("interfacerole", "Interface Roles"),
    _menu_item("interfaceroleassignment", "Assignments"),
    PluginMenuItem(
        link=f"plugins:{APP_LABEL}:rolesync_list",
        link_text="Synchronizations",
        permissions=[f"{APP_LABEL}.view_rolesync"],
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
