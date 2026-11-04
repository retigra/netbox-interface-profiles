"""
Search indexes for interface profiles.

This module defines search indexes to make plugin models searchable in NetBox's
global search. See: https://docs.netbox.dev/en/stable/plugins/development/search/
"""

from .interface_role import InterfaceRoleIndex
from .interface_role_assignment import InterfaceRoleAssignmentIndex
from .interface_template import InterfaceTemplateIndex
from .profile_config_template import ProfileConfigTemplateIndex
from .role_group import RoleGroupIndex

# Register all search indexes for this plugin
# The PluginConfig will automatically load these indexes
indexes = (
    InterfaceRoleIndex,
    InterfaceRoleAssignmentIndex,
    InterfaceTemplateIndex,
    ProfileConfigTemplateIndex,
    RoleGroupIndex,
)

__all__ = (
    "InterfaceRoleAssignmentIndex",
    "InterfaceRoleIndex",
    "InterfaceTemplateIndex",
    "ProfileConfigTemplateIndex",
    "RoleGroupIndex",
    "indexes",
)
