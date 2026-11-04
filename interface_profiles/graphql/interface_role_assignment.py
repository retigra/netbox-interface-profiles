"""
InterfaceRoleAssignment GraphQL schema for interface profiles.
"""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from netbox.graphql.types import NetBoxObjectType

from ..models import InterfaceRoleAssignment

if TYPE_CHECKING:
    from dcim.graphql.types import InterfaceType

    from .interface_role import InterfaceRoleType


@strawberry_django.type(
    InterfaceRoleAssignment,
    fields="__all__",
)
class InterfaceRoleAssignmentType(NetBoxObjectType):
    """GraphQL type for InterfaceRoleAssignment model."""

    interface: Annotated["InterfaceType", strawberry.lazy("dcim.graphql.types")]
    interface_role: Annotated["InterfaceRoleType", strawberry.lazy("interface_profiles.graphql.interface_role")]


@strawberry.type(name="Query")
class InterfaceRoleAssignmentQuery:
    """GraphQL queries for InterfaceRoleAssignment."""

    interface_role_assignment: InterfaceRoleAssignmentType = strawberry_django.field()
    interface_role_assignment_list: list[InterfaceRoleAssignmentType] = strawberry_django.field()
