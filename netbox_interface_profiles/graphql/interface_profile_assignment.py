"""
InterfaceProfileAssignment GraphQL schema for netbox interface profiles.
"""

import strawberry
import strawberry_django

from ..models import InterfaceProfileAssignment


@strawberry_django.type(
    InterfaceProfileAssignment,
    fields="__all__",
)
class InterfaceProfileAssignmentType:
    """GraphQL type for InterfaceProfileAssignment model."""

    pass


@strawberry.type(name="Query")
class InterfaceProfileAssignmentQuery:
    """GraphQL queries for InterfaceProfileAssignment."""

    interface_profile_assignment: InterfaceProfileAssignmentType = strawberry_django.field()
    interface_profile_assignment_list: list[InterfaceProfileAssignmentType] = strawberry_django.field()
