"""
Template extensions for interface profiles.
"""

from __future__ import annotations

from netbox.plugins import PluginTemplateExtension

from .models import ProfileConfigTemplate
from .services import get_matching_templates, resolve_interface_config


class DeviceHeadScripts(PluginTemplateExtension):
    """Inject plugin JS into the <head> of every page.

    head() is a global hook, so the script also runs on pages linking to the
    legacy Device interfaces tab, such as the Interface detail breadcrumb.
    """

    def head(self) -> str:
        return self.render("interface_profiles/remove_device_interface_tab.html")


class InterfaceRoleDetailCard(PluginTemplateExtension):
    """Render role assignment and matching templates on interface detail pages."""

    models = ["dcim.interface"]

    def right_page(self) -> str:
        interface = self.context["object"]

        resolved = resolve_interface_config(interface)
        role = resolved.interface_role
        matching_interface_templates = []
        matching_config_templates = []
        if role:
            matching_interface_templates = list(get_matching_templates(interface, role))
            matching_config_templates = list(ProfileConfigTemplate.objects.for_interface(interface, role))

        return self.render(
            "interface_profiles/inc/interface_role_detail_card.html",
            extra_context={
                "interface": interface,
                "assignment": resolved.assignment,
                "role": role,
                "matching_interface_templates": matching_interface_templates,
                "assigned_interface_template": resolved.interface_template,
                "matching_config_templates": matching_config_templates,
                "assigned_config_template": resolved.config_template,
                "assigned_config_preview": resolved.config
                if resolved.config_error is None
                else f"Unable to render config preview: {resolved.config_error}",
            },
        )


template_extensions = [DeviceHeadScripts, InterfaceRoleDetailCard]
