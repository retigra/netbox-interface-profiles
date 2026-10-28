"""Template tags for netbox interface profiles."""

from django import template
from django.db.models import Model
from django.utils.html import format_html, format_html_join
from django.utils.safestring import SafeString, mark_safe

register = template.Library()

PLACEHOLDER = mark_safe('<span class="text-muted">&mdash;</span>')


def _render_object(obj: Model) -> SafeString:
    if get_absolute_url := getattr(obj, "get_absolute_url", None):
        return format_html('<a href="{}">{}</a>', get_absolute_url(), obj)
    return format_html("{}", obj)


@register.simple_tag
def sync_value(value) -> SafeString:
    """Render an attribute value resolved by `describe_changes()`."""
    if value in (None, "", []):
        return PLACEHOLDER
    if isinstance(value, bool):
        return format_html("{}", "Yes" if value else "No")
    if isinstance(value, list):
        return format_html_join(", ", "{}", ((sync_value(item),) for item in value))
    if isinstance(value, Model):
        return _render_object(value)
    return format_html("{}", value)


@register.simple_tag
def template_attribute(template, field: str) -> SafeString:
    """Render an interface template attribute, indicating when synchronization clears it on the interface."""
    value = getattr(template, field)
    if value not in (None, ""):
        return format_html("{}", value)
    if template.is_set_null(field):
        return mark_safe('<span class="badge text-bg-warning" title="Cleared on the interface">Clear</span>')
    return PLACEHOLDER
