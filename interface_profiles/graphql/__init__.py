"""
GraphQL schema for interface profiles.

For more information on NetBox GraphQL, see:
https://docs.netbox.dev/en/stable/plugins/development/graphql/

For Strawberry GraphQL documentation, see:
https://strawberry.rocks/
"""

from .interface_role import InterfaceRoleQuery
from .interface_role_assignment import InterfaceRoleAssignmentQuery
from .interface_template import InterfaceTemplateQuery
from .profile_config_template import ProfileConfigTemplateQuery
from .role_group import RoleGroupQuery

schema = [
    InterfaceRoleQuery,
    InterfaceRoleAssignmentQuery,
    InterfaceTemplateQuery,
    ProfileConfigTemplateQuery,
    RoleGroupQuery,
]

__all__ = ("schema",)
