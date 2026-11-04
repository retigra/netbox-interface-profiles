"""
Views for interface profiles.

For more information on NetBox views, see:
https://docs.netbox.dev/en/stable/plugins/development/views/

For generic view classes, see:
https://docs.netbox.dev/en/stable/development/views/
"""

from .interface_role import (
    InterfaceRoleBulkDeleteView,
    InterfaceRoleBulkEditView,
    InterfaceRoleBulkImportView,
    InterfaceRoleDeleteView,
    InterfaceRoleEditView,
    InterfaceRoleInterfacesTabView,
    InterfaceRoleListView,
    InterfaceRoleSyncView,
    InterfaceRoleView,
)
from .interface_role_assignment import (
    DeviceInterfaceRoleTabView,
    InterfaceRoleAssignmentBulkDeleteView,
    InterfaceRoleAssignmentBulkEditView,
    InterfaceRoleAssignmentBulkImportView,
    InterfaceRoleAssignmentDeleteView,
    InterfaceRoleAssignmentEditView,
    InterfaceRoleAssignmentListView,
    InterfaceRoleAssignmentMenuHTMXView,
    InterfaceRoleAssignmentRemoveHTMXView,
    InterfaceRoleAssignmentSetHTMXView,
    InterfaceRoleAssignmentView,
)
from .interface_template import (
    InterfaceTemplateBulkDeleteView,
    InterfaceTemplateBulkEditView,
    InterfaceTemplateBulkImportView,
    InterfaceTemplateDeleteView,
    InterfaceTemplateEditView,
    InterfaceTemplateListView,
    InterfaceTemplateView,
)
from .profile_config_template import (
    ProfileConfigTemplateBulkDeleteView,
    ProfileConfigTemplateBulkEditView,
    ProfileConfigTemplateBulkImportView,
    ProfileConfigTemplateBulkSyncDataView,
    ProfileConfigTemplateDeleteView,
    ProfileConfigTemplateEditView,
    ProfileConfigTemplateListView,
    ProfileConfigTemplateView,
)
from .role_group import (
    RoleGroupBulkDeleteView,
    RoleGroupBulkEditView,
    RoleGroupBulkImportView,
    RoleGroupDeleteView,
    RoleGroupEditView,
    RoleGroupListView,
    RoleGroupView,
)
from .role_sync import (
    InterfaceRoleSyncsTabView,
    RoleSyncBulkDeleteView,
    RoleSyncDeleteView,
    RoleSyncListView,
    RoleSyncView,
)

__all__ = (
    "DeviceInterfaceRoleTabView",
    "InterfaceRoleAssignmentBulkDeleteView",
    "InterfaceRoleAssignmentBulkEditView",
    "InterfaceRoleAssignmentBulkImportView",
    "InterfaceRoleAssignmentDeleteView",
    "InterfaceRoleAssignmentEditView",
    "InterfaceRoleAssignmentListView",
    "InterfaceRoleAssignmentMenuHTMXView",
    "InterfaceRoleAssignmentRemoveHTMXView",
    "InterfaceRoleAssignmentSetHTMXView",
    "InterfaceRoleAssignmentView",
    "InterfaceRoleBulkDeleteView",
    "InterfaceRoleBulkEditView",
    "InterfaceRoleBulkImportView",
    "InterfaceRoleDeleteView",
    "InterfaceRoleEditView",
    "InterfaceRoleInterfacesTabView",
    "InterfaceRoleListView",
    "InterfaceRoleSyncView",
    "InterfaceRoleSyncsTabView",
    "InterfaceRoleView",
    "InterfaceTemplateBulkDeleteView",
    "InterfaceTemplateBulkEditView",
    "InterfaceTemplateBulkImportView",
    "InterfaceTemplateDeleteView",
    "InterfaceTemplateEditView",
    "InterfaceTemplateListView",
    "InterfaceTemplateView",
    "ProfileConfigTemplateBulkDeleteView",
    "ProfileConfigTemplateBulkEditView",
    "ProfileConfigTemplateBulkImportView",
    "ProfileConfigTemplateBulkSyncDataView",
    "ProfileConfigTemplateDeleteView",
    "ProfileConfigTemplateEditView",
    "ProfileConfigTemplateListView",
    "ProfileConfigTemplateView",
    "RoleGroupBulkDeleteView",
    "RoleGroupBulkEditView",
    "RoleGroupBulkImportView",
    "RoleGroupDeleteView",
    "RoleGroupEditView",
    "RoleGroupListView",
    "RoleGroupView",
    "RoleSyncBulkDeleteView",
    "RoleSyncDeleteView",
    "RoleSyncListView",
    "RoleSyncView",
)
