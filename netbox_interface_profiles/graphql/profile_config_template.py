"""
ProfileConfigTemplate GraphQL schema for netbox interface profiles.
"""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from netbox.graphql.types import NetBoxObjectType

from ..models import ProfileConfigTemplate

if TYPE_CHECKING:
    from dcim.graphql.types import DeviceTypeType, PlatformType

    from .interface_template import InterfaceProfileTemplateType


@strawberry_django.type(
    ProfileConfigTemplate,
    fields="__all__",
)
class ProfileConfigTemplateType(NetBoxObjectType):
    """GraphQL type for ProfileConfigTemplate model."""

    interface_template: Annotated[
        "InterfaceProfileTemplateType", strawberry.lazy("netbox_interface_profiles.graphql.interface_template")
    ]
    platform: Annotated["PlatformType", strawberry.lazy("dcim.graphql.types")]
    device_type: Annotated["DeviceTypeType", strawberry.lazy("dcim.graphql.types")] | None


@strawberry.type(name="Query")
class ProfileConfigTemplateQuery:
    """GraphQL queries for ProfileConfigTemplate."""

    profile_config_template: ProfileConfigTemplateType = strawberry_django.field()
    profile_config_template_list: list[ProfileConfigTemplateType] = strawberry_django.field()
