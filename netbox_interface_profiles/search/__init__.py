"""
Search indexes for netbox interface profiles.

This module defines search indexes to make plugin models searchable in NetBox's
global search. See: https://docs.netbox.dev/en/stable/plugins/development/search/
"""

from .interface_profile import InterfaceProfileIndex

# Register all search indexes for this plugin
# The PluginConfig will automatically load these indexes
indexes = (InterfaceProfileIndex,)

__all__ = (
    "InterfaceProfileIndex",
    "indexes",
)
