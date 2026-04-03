"""
Search indexes for netbox interface profiles.

This module defines search indexes to make plugin models searchable in NetBox's
global search. See: https://docs.netbox.dev/en/stable/plugins/development/search/
"""

from .interface_profile import InterfaceProfileIndex
from .interface_profile_assignment import InterfaceProfileAssignmentIndex
from .profile_config_template import ProfileConfigTemplateIndex

# Register all search indexes for this plugin
# The PluginConfig will automatically load these indexes
indexes = (
    InterfaceProfileIndex,
    InterfaceProfileAssignmentIndex,
    ProfileConfigTemplateIndex,
)

__all__ = (
    "InterfaceProfileAssignmentIndex",
    "InterfaceProfileIndex",
    "ProfileConfigTemplateIndex",
    "indexes",
)
