"""
InterfaceProfile GraphQL schema for netbox interface profiles.
"""

import strawberry
import strawberry_django

from ..models import InterfaceProfile


@strawberry_django.type(
    InterfaceProfile,
    fields="__all__",
)
class InterfaceProfileType:
    """GraphQL type for InterfaceProfile model."""

    pass


@strawberry.type(name="Query")
class InterfaceProfileQuery:
    """GraphQL queries for InterfaceProfile."""

    interface_profile: InterfaceProfileType = strawberry_django.field()
    interface_profile_list: list[InterfaceProfileType] = strawberry_django.field()
