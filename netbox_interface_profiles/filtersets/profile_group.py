"""
ProfileGroup filterset for netbox interface profiles.
"""

from netbox.filtersets import OrganizationalModelFilterSet

from ..models import ProfileGroup


class ProfileGroupFilterSet(OrganizationalModelFilterSet):
    """Filter set for ProfileGroup."""

    class Meta:
        model = ProfileGroup
        fields = ("id", "name", "slug", "description")
