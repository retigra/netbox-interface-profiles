"""
Forms for interface profiles.

For more information on NetBox forms, see:
https://docs.netbox.dev/en/stable/plugins/development/forms/
"""

from .interface_role import (
    InterfaceRoleBulkEditForm,
    InterfaceRoleFilterSetForm,
    InterfaceRoleForm,
    InterfaceRoleImportForm,
    InterfaceRoleSyncForm,
)
from .interface_role_assignment import (
    DeviceBulkAssignRoleForm,
    InterfaceRoleAssignmentBulkEditForm,
    InterfaceRoleAssignmentFilterSetForm,
    InterfaceRoleAssignmentForm,
    InterfaceRoleAssignmentImportForm,
)
from .interface_template import (
    InterfaceTemplateBulkEditForm,
    InterfaceTemplateFilterSetForm,
    InterfaceTemplateForm,
    InterfaceTemplateImportForm,
)
from .profile_config_template import (
    ProfileConfigTemplateBulkEditForm,
    ProfileConfigTemplateFilterSetForm,
    ProfileConfigTemplateForm,
    ProfileConfigTemplateImportForm,
)
from .role_group import (
    RoleGroupBulkEditForm,
    RoleGroupFilterSetForm,
    RoleGroupForm,
    RoleGroupImportForm,
)

__all__ = (
    "DeviceBulkAssignRoleForm",
    "InterfaceRoleAssignmentBulkEditForm",
    "InterfaceRoleAssignmentFilterSetForm",
    "InterfaceRoleAssignmentForm",
    "InterfaceRoleAssignmentImportForm",
    "InterfaceRoleBulkEditForm",
    "InterfaceRoleFilterSetForm",
    "InterfaceRoleForm",
    "InterfaceRoleImportForm",
    "InterfaceRoleSyncForm",
    "InterfaceTemplateBulkEditForm",
    "InterfaceTemplateFilterSetForm",
    "InterfaceTemplateForm",
    "InterfaceTemplateImportForm",
    "ProfileConfigTemplateBulkEditForm",
    "ProfileConfigTemplateFilterSetForm",
    "ProfileConfigTemplateForm",
    "ProfileConfigTemplateImportForm",
    "RoleGroupBulkEditForm",
    "RoleGroupFilterSetForm",
    "RoleGroupForm",
    "RoleGroupImportForm",
)
