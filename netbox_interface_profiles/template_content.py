"""
Template extensions for netbox interface profiles.
"""

from __future__ import annotations

from django.db.models import Case, IntegerField, Q, Value, When
from jinja2 import Environment
from netbox.plugins import PluginTemplateExtension

from .models import InterfaceTemplate, ProfileConfigTemplate


class DeviceHeadScripts(PluginTemplateExtension):
    """Inject plugin JS into the <head> of every Device object page.

    Scoping to 'dcim.device' means head() is called on the Device detail view
    and all tabs registered via register_model_view (including our own
    DeviceInterfaceProfileTabView), but not on the Device list view.
    """

    def head(self) -> str:
        return self.render("netbox_interface_profiles/remove_device_interface_tab.html")


def _render_config_preview(template_code: str, context: dict) -> str:
    """Render a config preview string from Jinja2 template code."""
    try:
        environment = Environment(autoescape=False)
        template = environment.from_string(template_code)
        return template.render(context)
    except Exception as exc:  # pragma: no cover - defensive for user-authored templates
        return f"Unable to render config preview: {exc}"


class InterfaceProfileDetailCard(PluginTemplateExtension):
    """Render profile assignment and matching templates on interface detail pages."""

    models = ["dcim.interface"]

    def right_page(self) -> str:
        interface = self.context["object"]

        assignment = getattr(interface, "profile_assignment", None)
        profile = getattr(assignment, "interface_profile", None)

        matching_interface_templates = []
        assigned_interface_template = None
        matching_config_templates = []
        assigned_config_template = None
        assigned_config_preview = ""

        if profile:
            site_group_id = getattr(interface.device.site, "group_id", None)
            interface_templates = InterfaceTemplate.objects.filter(interface_profile=profile)
            if site_group_id:
                interface_templates = interface_templates.filter(
                    Q(site_group_id=site_group_id) | Q(site_group__isnull=True)
                )
            else:
                interface_templates = interface_templates.filter(site_group__isnull=True)

            matching_interface_templates = list(
                interface_templates.order_by(
                    Case(
                        When(site_group_id=site_group_id, then=Value(0)),
                        default=Value(1),
                        output_field=IntegerField(),
                    ),
                    "pk",
                )
            )
            if matching_interface_templates:
                assigned_interface_template = matching_interface_templates[0]

            if interface.device.platform is not None:
                config_templates = ProfileConfigTemplate.objects.filter(
                    interface_profile=profile,
                    platform=interface.device.platform,
                )
                config_templates = config_templates.filter(
                    Q(device_type=interface.device.device_type) | Q(device_type__isnull=True)
                )

                matching_config_templates = list(
                    config_templates.order_by(
                        Case(
                            When(device_type=interface.device.device_type, then=Value(0)),
                            default=Value(1),
                            output_field=IntegerField(),
                        ),
                        "name",
                        "pk",
                    )
                )
                if matching_config_templates:
                    assigned_config_template = matching_config_templates[0]
                    assigned_config_preview = _render_config_preview(
                        assigned_config_template.template_code,
                        {
                            "interface": interface,
                            "device": interface.device,
                            "profile": profile,
                            "assignment": assignment,
                            "config_template": assigned_config_template,
                        },
                    )

        return self.render(
            "netbox_interface_profiles/inc/interface_profile_detail_card.html",
            extra_context={
                "interface": interface,
                "assignment": assignment,
                "profile": profile,
                "matching_interface_templates": matching_interface_templates,
                "assigned_interface_template": assigned_interface_template,
                "matching_config_templates": matching_config_templates,
                "assigned_config_template": assigned_config_template,
                "assigned_config_preview": assigned_config_preview,
            },
        )


template_extensions = [DeviceHeadScripts, InterfaceProfileDetailCard]
