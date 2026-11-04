"""
RoleGroup filterset for interface profiles.
"""

from netbox.filtersets import OrganizationalModelFilterSet

from ..models import RoleGroup


class RoleGroupFilterSet(OrganizationalModelFilterSet):
    """Filter set for RoleGroup."""

    class Meta:
        model = RoleGroup
        fields = ("id", "name", "slug", "description")
