"""
Template extensions for netbox interface profiles.
"""

from __future__ import annotations

from dcim.models import Site, SiteGroup
from django.contrib.contenttypes.models import ContentType
from django.db.models import Case, IntegerField, Q, Value, When
from jinja2 import Environment
from netbox.plugins import PluginTemplateExtension

from .models import InterfaceTemplate, ProfileConfigTemplate


class DeviceHeadScripts(PluginTemplateExtension):
    """Inject plugin JS into the <head> of every page.

    head() is a global hook, so the script also runs on pages linking to the
    legacy Device interfaces tab, such as the Interface detail breadcrumb.
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


class InterfaceRoleDetailCard(PluginTemplateExtension):
    """Render role assignment and matching templates on interface detail pages."""

    models = ["dcim.interface"]

    def right_page(self) -> str:
        interface = self.context["object"]

        assignment = getattr(interface, "role_assignment", None)
        role = getattr(assignment, "interface_role", None)

        matching_interface_templates = []
        assigned_interface_template = None
        matching_config_templates = []
        assigned_config_template = None
        assigned_config_preview = ""

        if role:
            site = interface.device.site
            site_group = getattr(site, "group", None)
            site_ct = ContentType.objects.get_for_model(Site)
            site_group_ct = ContentType.objects.get_for_model(SiteGroup)

            scope_q = Q(scope_type__isnull=True)  # global
            if site:
                scope_q |= Q(scope_type=site_ct, scope_id=site.pk)
            if site_group:
                scope_q |= Q(scope_type=site_group_ct, scope_id=site_group.pk)

            interface_templates = InterfaceTemplate.objects.filter(interface_role=role).filter(scope_q)

            matching_interface_templates = list(
                interface_templates.annotate(
                    scope_priority=Case(
                        When(scope_type=site_ct, then=Value(0)),
                        When(scope_type=site_group_ct, then=Value(1)),
                        default=Value(2),
                        output_field=IntegerField(),
                    )
                ).order_by("scope_priority", "pk")
            )
            if matching_interface_templates:
                assigned_interface_template = matching_interface_templates[0]

            if interface.device.platform is not None:
                config_templates = ProfileConfigTemplate.objects.filter(
                    interface_template__interface_role=role,
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
                            "role": role,
                            "assignment": assignment,
                            "config_template": assigned_config_template,
                        },
                    )

        return self.render(
            "netbox_interface_profiles/inc/interface_role_detail_card.html",
            extra_context={
                "interface": interface,
                "assignment": assignment,
                "role": role,
                "matching_interface_templates": matching_interface_templates,
                "assigned_interface_template": assigned_interface_template,
                "matching_config_templates": matching_config_templates,
                "assigned_config_template": assigned_config_template,
                "assigned_config_preview": assigned_config_preview,
            },
        )


template_extensions = [DeviceHeadScripts, InterfaceRoleDetailCard]
