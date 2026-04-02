"""
ProfileConfigTemplate GraphQL schema for netbox interface profiles.
"""

import strawberry
import strawberry_django

from ..models import ProfileConfigTemplate


@strawberry_django.type(
    ProfileConfigTemplate,
    fields="__all__",
)
class ProfileConfigTemplateType:
    """GraphQL type for ProfileConfigTemplate model."""

    pass


@strawberry.type(name="Query")
class ProfileConfigTemplateQuery:
    """GraphQL queries for ProfileConfigTemplate."""

    profile_config_template: ProfileConfigTemplateType = strawberry_django.field()
    profile_config_template_list: list[ProfileConfigTemplateType] = strawberry_django.field()
