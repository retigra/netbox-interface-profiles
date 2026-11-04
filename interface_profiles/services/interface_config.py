"""Resolve and render the configuration of a single interface."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..models import InterfaceRole, InterfaceRoleAssignment, InterfaceTemplate, ProfileConfigTemplate
from .role_sync import get_matching_templates


@dataclass
class InterfaceConfig:
    """The role of an interface, the templates that apply to it and its rendered configuration."""

    interface: Any
    assignment: InterfaceRoleAssignment | None = None
    interface_template: InterfaceTemplate | None = None
    config_template: ProfileConfigTemplate | None = None
    config: str | None = None
    config_error: str | None = None

    @property
    def interface_role(self) -> InterfaceRole | None:
        return getattr(self.assignment, "interface_role", None)


def get_render_context(interface, assignment=None, config_template=None, device_context=None) -> dict[str, Any]:
    """Return the context a config template is rendered with outside of a device config template.

    This mirrors rendering through `interface_config_render()` in a device config template: the device's config
    context data and `device`, plus `interface`. The interface's `role`, `assignment` and the `config_template` are
    added for convenience.
    """
    device = interface.device
    if device_context is None:
        device_context = device.get_config_context()

    return {
        **device_context,
        "device": device,
        "interface": interface,
        "role": getattr(assignment, "interface_role", None),
        "assignment": assignment,
        "config_template": config_template,
    }


def resolve_interface_config(interface, assignment=None, render: bool = True, device_context=None) -> InterfaceConfig:
    """Resolve the role, interface template and config template of an interface, and render its configuration.

    `assignment` defaults to the role assignment of the interface. Rendering errors are returned in `config_error`
    rather than raised, so a single broken template does not prevent resolving other interfaces.
    """
    if assignment is None:
        assignment = getattr(interface, "role_assignment", None)

    result = InterfaceConfig(interface=interface, assignment=assignment)
    role = result.interface_role
    if role is None:
        return result

    result.interface_template = get_matching_templates(interface, role).first()
    result.config_template = ProfileConfigTemplate.objects.for_interface(interface, role).first()

    if render and result.config_template is not None:
        context = get_render_context(interface, assignment, result.config_template, device_context)
        try:
            result.config = result.config_template.render(context)
        except Exception as exc:
            result.config_error = result.config_template.format_render_error(exc)

    return result
