"""
GraphQL schema for netbox interface profiles.

For more information on NetBox GraphQL, see:
https://docs.netbox.dev/en/stable/plugins/development/graphql/

For Strawberry GraphQL documentation, see:
https://strawberry.rocks/
"""

from .interface_profile import InterfaceProfileQuery
from .profile_config_template import ProfileConfigTemplateQuery

schema = [
    InterfaceProfileQuery,
    ProfileConfigTemplateQuery,
]

__all__ = ("schema",)
