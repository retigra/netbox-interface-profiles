"""
InterfaceProfile GraphQL schema for netbox interface profiles.
"""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from netbox.graphql.types import NetBoxObjectType

from ..models import InterfaceProfile

if TYPE_CHECKING:
    from dcim.graphql.types import DeviceRoleType

    from .interface_profile_assignment import InterfaceProfileAssignmentType
    from .interface_template import InterfaceProfileTemplateType
    from .profile_group import ProfileGroupType


@strawberry_django.type(
    InterfaceProfile,
    fields="__all__",
)
class InterfaceProfileType(NetBoxObjectType):
    """GraphQL type for InterfaceProfile model."""

    group: Annotated["ProfileGroupType", strawberry.lazy("netbox_interface_profiles.graphql.profile_group")] | None
    device_roles: list[Annotated["DeviceRoleType", strawberry.lazy("dcim.graphql.types")]]
    interface_templates: list[
        Annotated[
            "InterfaceProfileTemplateType", strawberry.lazy("netbox_interface_profiles.graphql.interface_template")
        ]
    ]
    interface_assignments: list[
        Annotated[
            "InterfaceProfileAssignmentType",
            strawberry.lazy("netbox_interface_profiles.graphql.interface_profile_assignment"),
        ]
    ]


@strawberry.type(name="Query")
class InterfaceProfileQuery:
    """GraphQL queries for InterfaceProfile."""

    interface_profile: InterfaceProfileType = strawberry_django.field()
    interface_profile_list: list[InterfaceProfileType] = strawberry_django.field()
