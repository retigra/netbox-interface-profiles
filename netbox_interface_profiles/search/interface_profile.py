"""
InterfaceProfile search index for netbox interface profiles.
"""

from netbox.search import SearchIndex

from ..models import InterfaceProfile


class InterfaceProfileIndex(SearchIndex):
    """
    Search index for InterfaceProfile model.

    Enables InterfaceProfile objects to appear in NetBox's global search
    results, matched by name and description fields.
    """

    model = InterfaceProfile
    fields = (
        ("name", 100),
        ("description", 500),
    )
    display_attrs = (
        "name",
        "description",
    )
