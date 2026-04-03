"""
InterfaceProfileAssignment search index for netbox interface profiles.
"""

from netbox.search import SearchIndex

from ..models import InterfaceProfileAssignment


class InterfaceProfileAssignmentIndex(SearchIndex):
    """
    Search index for InterfaceProfileAssignment.

    Surfaces assignments in global search by the interface and profile names.
    """

    model = InterfaceProfileAssignment
    fields = ()
    display_attrs = (
        "interface",
        "interface_profile",
    )
