"""
Jinja2 helpers exposed to NetBox config templates.
"""

from jinja2 import pass_context


@pass_context
def interface_render(context, interface, **extra_context):
    """
    Render the config template applicable to an interface, or an empty string when none applies.

    The interface template receives the context of the calling template (e.g. `device` and the config context
    of a device config template), with `interface` and any keyword arguments added.
    """
    from .models import ProfileConfigTemplate

    template = ProfileConfigTemplate.objects.for_interface(interface).first()
    if template is None:
        return ""

    return template.render({**context.get_all(), **extra_context, "interface": interface})


context = {
    "interface_render": interface_render,
}
