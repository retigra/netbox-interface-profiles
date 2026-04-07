"""
InterfaceTemplate GraphQL schema for netbox interface profiles.
"""

import strawberry
import strawberry_django

from ..models import InterfaceTemplate


@strawberry_django.type(
    InterfaceTemplate,
    fields="__all__",
)
class InterfaceTemplateType:
    """GraphQL type for InterfaceTemplate model."""

    pass


@strawberry.type(name="Query")
class InterfaceTemplateQuery:
    """GraphQL queries for InterfaceTemplate."""

    interface_template: InterfaceTemplateType = strawberry_django.field()
    interface_template_list: list[InterfaceTemplateType] = strawberry_django.field()
