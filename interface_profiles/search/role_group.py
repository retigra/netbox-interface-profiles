"""
RoleGroup search index for interface profiles.
"""

from netbox.search import SearchIndex

from ..models import RoleGroup


class RoleGroupIndex(SearchIndex):
    """
    Search index for RoleGroup model.

    Enables RoleGroup objects to appear in NetBox's global search
    results, matched by name, slug and description fields.
    """

    model = RoleGroup
    fields = (
        ("name", 100),
        ("slug", 110),
        ("description", 500),
        ("comments", 5000),
    )
    display_attrs = ("description",)
