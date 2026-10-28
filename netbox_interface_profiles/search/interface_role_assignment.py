"""
InterfaceRoleAssignment search index for netbox interface profiles.
"""

from netbox.search import SearchIndex

from ..models import InterfaceRoleAssignment


class InterfaceRoleAssignmentIndex(SearchIndex):
    """
    Search index for InterfaceRoleAssignment.

    Surfaces assignments in global search by the interface and role names.
    """

    model = InterfaceRoleAssignment
    fields = ()
    display_attrs = (
        "interface",
        "interface_role",
    )
