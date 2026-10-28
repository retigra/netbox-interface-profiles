"""
ProfileConfigTemplate GraphQL schema for netbox interface profiles.
"""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from core.graphql.mixins import SyncedDataMixin
from netbox.graphql.types import NetBoxObjectType

from ..models import ProfileConfigTemplate

if TYPE_CHECKING:
    from dcim.graphql.types import DeviceTypeType, PlatformType
    from extras.graphql.types import TagType

    from .interface_role import InterfaceRoleType


@strawberry_django.type(
    ProfileConfigTemplate,
    fields="__all__",
)
class ProfileConfigTemplateType(SyncedDataMixin, NetBoxObjectType):
    """GraphQL type for ProfileConfigTemplate model."""

    interface_role: Annotated["InterfaceRoleType", strawberry.lazy("netbox_interface_profiles.graphql.interface_role")]
    platform: Annotated["PlatformType", strawberry.lazy("dcim.graphql.types")]
    device_type: Annotated["DeviceTypeType", strawberry.lazy("dcim.graphql.types")] | None
    device_tags: list[Annotated["TagType", strawberry.lazy("extras.graphql.types")]]
    interface_tags: list[Annotated["TagType", strawberry.lazy("extras.graphql.types")]]


@strawberry.type(name="Query")
class ProfileConfigTemplateQuery:
    """GraphQL queries for ProfileConfigTemplate."""

    profile_config_template: ProfileConfigTemplateType = strawberry_django.field()
    profile_config_template_list: list[ProfileConfigTemplateType] = strawberry_django.field()
