"""
InterfaceProfileAssignment GraphQL schema for netbox interface profiles.
"""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from netbox.graphql.types import NetBoxObjectType

from ..models import InterfaceProfileAssignment

if TYPE_CHECKING:
    from dcim.graphql.types import InterfaceType

    from .interface_profile import InterfaceProfileType


@strawberry_django.type(
    InterfaceProfileAssignment,
    fields="__all__",
)
class InterfaceProfileAssignmentType(NetBoxObjectType):
    """GraphQL type for InterfaceProfileAssignment model."""

    interface: Annotated["InterfaceType", strawberry.lazy("dcim.graphql.types")]
    interface_profile: Annotated[
        "InterfaceProfileType", strawberry.lazy("netbox_interface_profiles.graphql.interface_profile")
    ]


@strawberry.type(name="Query")
class InterfaceProfileAssignmentQuery:
    """GraphQL queries for InterfaceProfileAssignment."""

    interface_profile_assignment: InterfaceProfileAssignmentType = strawberry_django.field()
    interface_profile_assignment_list: list[InterfaceProfileAssignmentType] = strawberry_django.field()
