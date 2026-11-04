"""
ProfileConfigTemplate search index for interface profiles.
"""

from netbox.search import SearchIndex

from ..models import ProfileConfigTemplate


class ProfileConfigTemplateIndex(SearchIndex):
    """
    Search index for ProfileConfigTemplate model.

    Enables ProfileConfigTemplate objects to appear in NetBox's global search
    results, matched by name, description, and template_code fields.
    """

    model = ProfileConfigTemplate
    fields = (
        ("name", 100),
        ("description", 500),
        ("template_code", 1000),
    )
    display_attrs = (
        "name",
        "interface_role",
        "platform",
        "device_type",
    )
