"""
RoleGroup GraphQL schema for netbox interface profiles.
"""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from netbox.graphql.types import OrganizationalObjectType

from ..models import RoleGroup

if TYPE_CHECKING:
    from .interface_role import InterfaceRoleType


@strawberry_django.type(
    RoleGroup,
    fields="__all__",
)
class RoleGroupType(OrganizationalObjectType):
    """GraphQL type for RoleGroup model."""

    interface_roles: list[
        Annotated["InterfaceRoleType", strawberry.lazy("netbox_interface_profiles.graphql.interface_role")]
    ]


@strawberry.type(name="Query")
class RoleGroupQuery:
    """GraphQL queries for RoleGroup."""

    role_group: RoleGroupType = strawberry_django.field()
    role_group_list: list[RoleGroupType] = strawberry_django.field()
