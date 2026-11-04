"""
Models for interface profiles.

For more information on NetBox models, see:
https://docs.netbox.dev/en/stable/plugins/development/models/

For NetBox model features (tags, custom fields, change logging, etc.), see:
https://docs.netbox.dev/en/stable/development/models/#netbox-model-features
"""

from .interface_role import InterfaceRole
from .interface_role_assignment import InterfaceRoleAssignment
from .interface_template import InterfaceTemplate
from .profile_config_template import ProfileConfigTemplate
from .role_group import RoleGroup
from .role_sync import RoleSync, RoleSyncChange

__all__ = (
    "InterfaceRole",
    "InterfaceRoleAssignment",
    "InterfaceTemplate",
    "ProfileConfigTemplate",
    "RoleGroup",
    "RoleSync",
    "RoleSyncChange",
)
