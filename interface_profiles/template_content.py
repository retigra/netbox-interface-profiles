"""
Template extensions for interface profiles.
"""

from __future__ import annotations

from netbox.plugins import PluginTemplateExtension

from .models import InterfaceRoleAssignment, ProfileConfigTemplate
from .services import get_matching_templates, resolve_interface_config


class DeviceHeadScripts(PluginTemplateExtension):
    """Inject plugin JS into the <head> of every page.

    head() is a global hook, so the script also runs on pages linking to the
    legacy Device interfaces tab, such as the Interface detail breadcrumb.
    """

    def head(self) -> str:
        return self.render("interface_profiles/remove_device_interface_tab.html")


class InterfaceRoleDetailCard(PluginTemplateExtension):
    """Render role assignment and matching templates on interface detail pages.

    The card is only shown to users who may view the interface's role assignment. It lists only the templates the
    user may view, and renders the config preview only when the user may view the config template producing it.
    """

    models = ["dcim.interface"]

    def right_page(self) -> str:
        user = self.context["request"].user
        if not user.has_perm("interface_profiles.view_interfaceroleassignment"):
            return ""

        interface = self.context["object"]
        assignment = (
            InterfaceRoleAssignment.objects.restrict(user, "view")
            .select_related("interface_role__group")
            .filter(interface=interface)
            .first()
        )
        if assignment is None and InterfaceRoleAssignment.objects.filter(interface=interface).exists():
            # The interface has an assignment outside the user's view constraints
            return ""

        matching_interface_templates = []
        matching_config_templates = []
        if role := getattr(assignment, "interface_role", None):
            matching_interface_templates = list(get_matching_templates(interface, role).restrict(user, "view"))
            matching_config_templates = list(
                ProfileConfigTemplate.objects.for_interface(interface, role).restrict(user, "view")
            )

        resolved = resolve_interface_config(interface, assignment=assignment, render=False)
        can_view_config = resolved.config_template in matching_config_templates
        if can_view_config:
            resolved = resolve_interface_config(interface, assignment=assignment)

        return self.render(
            "interface_profiles/inc/interface_role_detail_card.html",
            extra_context={
                "interface": interface,
                "assignment": assignment,
                "role": role,
                "matching_interface_templates": matching_interface_templates,
                "assigned_interface_template": resolved.interface_template,
                "matching_config_templates": matching_config_templates,
                "assigned_config_template": resolved.config_template if can_view_config else None,
                "assigned_config_preview": resolved.config
                if resolved.config_error is None
                else f"Unable to render config preview: {resolved.config_error}",
            },
        )


template_extensions = [DeviceHeadScripts, InterfaceRoleDetailCard]
