"""
InterfaceTemplate GraphQL schema for interface profiles.

The type and query names are prefixed with "interface_role" to avoid
colliding with NetBox's core dcim InterfaceTemplateType and its queries.
"""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from netbox.graphql.types import NetBoxObjectType

from ..models import InterfaceTemplate

if TYPE_CHECKING:
    from dcim.graphql.types import SiteGroupType, SiteType
    from ipam.graphql.types import VLANTranslationPolicyType, VRFType
    from netbox.graphql.types import ContentTypeType

    from .interface_role import InterfaceRoleType


@strawberry_django.type(
    InterfaceTemplate,
    fields="__all__",
    name="InterfaceRoleTemplateType",
)
class InterfaceRoleTemplateType(NetBoxObjectType):
    """GraphQL type for InterfaceTemplate model."""

    interface_role: Annotated["InterfaceRoleType", strawberry.lazy("interface_profiles.graphql.interface_role")]
    scope_type: Annotated["ContentTypeType", strawberry.lazy("netbox.graphql.types")] | None
    scope_sites: list[Annotated["SiteType", strawberry.lazy("dcim.graphql.types")]]
    scope_site_groups: list[Annotated["SiteGroupType", strawberry.lazy("dcim.graphql.types")]]
    vrf: Annotated["VRFType", strawberry.lazy("ipam.graphql.types")] | None
    vlan_translation_policy: Annotated["VLANTranslationPolicyType", strawberry.lazy("ipam.graphql.types")] | None


@strawberry.type(name="Query")
class InterfaceTemplateQuery:
    """GraphQL queries for InterfaceTemplate."""

    interface_role_template: InterfaceRoleTemplateType = strawberry_django.field()
    interface_role_template_list: list[InterfaceRoleTemplateType] = strawberry_django.field()
