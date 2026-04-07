"""
GraphQL schema for netbox interface profiles.

For more information on NetBox GraphQL, see:
https://docs.netbox.dev/en/stable/plugins/development/graphql/

For Strawberry GraphQL documentation, see:
https://strawberry.rocks/
"""

from .interface_profile import InterfaceProfileQuery
from .interface_profile_assignment import InterfaceProfileAssignmentQuery
from .interface_template import InterfaceTemplateQuery
from .profile_config_template import ProfileConfigTemplateQuery

schema = [
    InterfaceProfileQuery,
    InterfaceProfileAssignmentQuery,
    InterfaceTemplateQuery,
    ProfileConfigTemplateQuery,
]

__all__ = ("schema",)
