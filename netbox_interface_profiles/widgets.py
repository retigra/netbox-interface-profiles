"""
Custom form widgets for netbox interface profiles.
"""

from django import forms
from django.utils.html import format_html


class ProfileNameWidget(forms.TextInput):
    """
    TextInput with a "Generate" button that computes a slugified name from the
    three scope fields: platform, (optional) device_type, and interface_profile.

    The generated slug follows the pattern:
        {platform}-{device_type}-{interface_profile}
    omitting device_type when it is not selected.

    Requires profile_name_widget.js, which is loaded globally via
    PluginTemplateExtension.head() in template_content.py.
    """

    def render(self, name: str, value, attrs: dict | None = None, renderer=None) -> str:
        """Wrap the standard text input in a Bootstrap input-group with a Generate button."""
        input_html = super().render(name, value, attrs, renderer)
        return format_html(
            '<div class="input-group">'
            "{}"
            '<button type="button" class="btn btn-secondary" '
            'id="btn-generate-profile-name" '
            'title="Generate name from Platform, Device Type and Interface Profile">'
            '<i class="mdi mdi-refresh"></i>'
            "</button>"
            "</div>",
            input_html,
        )
