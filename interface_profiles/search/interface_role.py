"""
InterfaceRole search index for interface profiles.
"""

from netbox.search import SearchIndex

from ..models import InterfaceRole


class InterfaceRoleIndex(SearchIndex):
    """
    Search index for InterfaceRole model.

    Enables InterfaceRole objects to appear in NetBox's global search
    results, matched by name and description fields.
    """

    model = InterfaceRole
    fields = (
        ("name", 100),
        ("description", 500),
    )
    display_attrs = (
        "name",
        "description",
    )
