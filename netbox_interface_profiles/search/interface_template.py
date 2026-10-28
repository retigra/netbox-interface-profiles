"""
InterfaceTemplate search index for netbox interface profiles.
"""

from netbox.search import SearchIndex

from ..models import InterfaceTemplate


class InterfaceTemplateIndex(SearchIndex):
    """
    Search index for InterfaceTemplate model.

    Enables InterfaceTemplate objects to appear in NetBox's global search
    results, matched by name and description fields.
    """

    model = InterfaceTemplate
    fields = (
        ("name", 100),
        ("description", 500),
    )
    display_attrs = (
        "name",
        "interface_role",
        "scope",
    )
