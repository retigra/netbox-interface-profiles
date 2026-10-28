"""
InterfaceRole GraphQL schema for netbox interface profiles.
"""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from netbox.graphql.types import NetBoxObjectType

from ..models import InterfaceRole

if TYPE_CHECKING:
    from dcim.graphql.types import DeviceRoleType

    from .interface_role_assignment import InterfaceRoleAssignmentType
    from .interface_template import InterfaceRoleTemplateType
    from .profile_config_template import ProfileConfigTemplateType
    from .role_group import RoleGroupType


@strawberry_django.type(
    InterfaceRole,
    fields="__all__",
)
class InterfaceRoleType(NetBoxObjectType):
    """GraphQL type for InterfaceRole model."""

    group: Annotated["RoleGroupType", strawberry.lazy("netbox_interface_profiles.graphql.role_group")] | None
    device_roles: list[Annotated["DeviceRoleType", strawberry.lazy("dcim.graphql.types")]]
    interface_templates: list[
        Annotated["InterfaceRoleTemplateType", strawberry.lazy("netbox_interface_profiles.graphql.interface_template")]
    ]
    config_templates: list[
        Annotated[
            "ProfileConfigTemplateType",
            strawberry.lazy("netbox_interface_profiles.graphql.profile_config_template"),
        ]
    ]
    interface_assignments: list[
        Annotated[
            "InterfaceRoleAssignmentType",
            strawberry.lazy("netbox_interface_profiles.graphql.interface_role_assignment"),
        ]
    ]


@strawberry.type(name="Query")
class InterfaceRoleQuery:
    """GraphQL queries for InterfaceRole."""

    interface_role: InterfaceRoleType = strawberry_django.field()
    interface_role_list: list[InterfaceRoleType] = strawberry_django.field()
