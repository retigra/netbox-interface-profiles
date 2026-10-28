"""
Tables for netbox interface profiles.

For more information on NetBox tables, see:
https://docs.netbox.dev/en/stable/plugins/development/tables/

For django-tables2 documentation, see:
https://django-tables2.readthedocs.io/
"""

from .interface_role import InterfaceRoleTable
from .interface_role_assignment import DeviceInterfaceTable, InterfaceRoleAssignmentTable
from .interface_template import InterfaceTemplateTable
from .profile_config_template import ProfileConfigTemplateTable
from .role_group import RoleGroupTable
from .role_sync import RoleSyncTable

__all__ = (
    "DeviceInterfaceTable",
    "InterfaceRoleAssignmentTable",
    "InterfaceRoleTable",
    "InterfaceTemplateTable",
    "ProfileConfigTemplateTable",
    "RoleGroupTable",
    "RoleSyncTable",
)
