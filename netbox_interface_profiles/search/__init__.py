"""
Search indexes for netbox interface profiles.

This module defines search indexes to make plugin models searchable in NetBox's
global search. See: https://docs.netbox.dev/en/stable/plugins/development/search/
"""

from .interface_profile import InterfaceProfileIndex
from .interface_profile_assignment import InterfaceProfileAssignmentIndex
from .interface_template import InterfaceTemplateIndex
from .profile_config_template import ProfileConfigTemplateIndex
from .profile_group import ProfileGroupIndex

# Register all search indexes for this plugin
# The PluginConfig will automatically load these indexes
indexes = (
    InterfaceProfileIndex,
    InterfaceProfileAssignmentIndex,
    InterfaceTemplateIndex,
    ProfileConfigTemplateIndex,
    ProfileGroupIndex,
)

__all__ = (
    "InterfaceProfileAssignmentIndex",
    "InterfaceProfileIndex",
    "InterfaceTemplateIndex",
    "ProfileConfigTemplateIndex",
    "ProfileGroupIndex",
    "indexes",
)
