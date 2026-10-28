"""
InterfaceTemplate GraphQL schema for netbox interface profiles.

The type and query names are prefixed with "interface_role" to avoid
colliding with NetBox's core dcim InterfaceTemplateType and its queries.
"""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from netbox.graphql.types import NetBoxObjectType

from ..models import InterfaceTemplate

if TYPE_CHECKING:
    from netbox.graphql.types import ContentTypeType

    from .interface_role import InterfaceRoleType
    from .profile_config_template import ProfileConfigTemplateType


@strawberry_django.type(
    InterfaceTemplate,
    fields="__all__",
    name="InterfaceRoleTemplateType",
)
class InterfaceRoleTemplateType(NetBoxObjectType):
    """GraphQL type for InterfaceTemplate model."""

    interface_role: Annotated["InterfaceRoleType", strawberry.lazy("netbox_interface_profiles.graphql.interface_role")]
    scope_type: Annotated["ContentTypeType", strawberry.lazy("netbox.graphql.types")] | None
    config_templates: list[
        Annotated[
            "ProfileConfigTemplateType",
            strawberry.lazy("netbox_interface_profiles.graphql.profile_config_template"),
        ]
    ]


@strawberry.type(name="Query")
class InterfaceTemplateQuery:
    """GraphQL queries for InterfaceTemplate."""

    interface_role_template: InterfaceRoleTemplateType = strawberry_django.field()
    interface_role_template_list: list[InterfaceRoleTemplateType] = strawberry_django.field()
