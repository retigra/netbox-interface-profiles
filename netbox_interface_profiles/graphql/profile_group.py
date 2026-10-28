"""
ProfileGroup GraphQL schema for netbox interface profiles.
"""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from netbox.graphql.types import OrganizationalObjectType

from ..models import ProfileGroup

if TYPE_CHECKING:
    from .interface_profile import InterfaceProfileType


@strawberry_django.type(
    ProfileGroup,
    fields="__all__",
)
class ProfileGroupType(OrganizationalObjectType):
    """GraphQL type for ProfileGroup model."""

    interface_profiles: list[
        Annotated["InterfaceProfileType", strawberry.lazy("netbox_interface_profiles.graphql.interface_profile")]
    ]


@strawberry.type(name="Query")
class ProfileGroupQuery:
    """GraphQL queries for ProfileGroup."""

    profile_group: ProfileGroupType = strawberry_django.field()
    profile_group_list: list[ProfileGroupType] = strawberry_django.field()
