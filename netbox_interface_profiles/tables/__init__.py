"""
Tables for netbox interface profiles.

For more information on NetBox tables, see:
https://docs.netbox.dev/en/stable/plugins/development/tables/

For django-tables2 documentation, see:
https://django-tables2.readthedocs.io/
"""

from .interface_profile import InterfaceProfileTable
from .interface_profile_assignment import DeviceInterfaceTable, InterfaceProfileAssignmentTable
from .interface_template import InterfaceTemplateTable
from .profile_config_template import ProfileConfigTemplateTable
from .profile_group import ProfileGroupTable
from .profile_sync import ProfileSyncTable

__all__ = (
    "DeviceInterfaceTable",
    "InterfaceProfileAssignmentTable",
    "InterfaceProfileTable",
    "InterfaceTemplateTable",
    "ProfileConfigTemplateTable",
    "ProfileGroupTable",
    "ProfileSyncTable",
)
