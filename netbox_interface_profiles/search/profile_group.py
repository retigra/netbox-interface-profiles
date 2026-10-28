"""
ProfileGroup search index for netbox interface profiles.
"""

from netbox.search import SearchIndex

from ..models import ProfileGroup


class ProfileGroupIndex(SearchIndex):
    """
    Search index for ProfileGroup model.

    Enables ProfileGroup objects to appear in NetBox's global search
    results, matched by name, slug and description fields.
    """

    model = ProfileGroup
    fields = (
        ("name", 100),
        ("slug", 110),
        ("description", 500),
        ("comments", 5000),
    )
    display_attrs = ("description",)
