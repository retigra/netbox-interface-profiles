"""
Views for netbox interface profiles.

For more information on NetBox views, see:
https://docs.netbox.dev/en/stable/plugins/development/views/

For generic view classes, see:
https://docs.netbox.dev/en/stable/development/views/
"""

from .interface_profile import (
    InterfaceProfileBulkDeleteView,
    InterfaceProfileBulkEditView,
    InterfaceProfileBulkImportView,
    InterfaceProfileDeleteView,
    InterfaceProfileEditView,
    InterfaceProfileListView,
    InterfaceProfileSyncView,
    InterfaceProfileView,
)
from .interface_profile_assignment import (
    DeviceInterfaceProfileTabView,
    InterfaceProfileAssignmentBulkDeleteView,
    InterfaceProfileAssignmentBulkEditView,
    InterfaceProfileAssignmentBulkImportView,
    InterfaceProfileAssignmentDeleteView,
    InterfaceProfileAssignmentEditView,
    InterfaceProfileAssignmentListView,
    InterfaceProfileAssignmentMenuHTMXView,
    InterfaceProfileAssignmentRemoveHTMXView,
    InterfaceProfileAssignmentSetHTMXView,
    InterfaceProfileAssignmentView,
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
    ProfileConfigTemplateDeleteView,
    ProfileConfigTemplateEditView,
    ProfileConfigTemplateListView,
    ProfileConfigTemplateView,
)

__all__ = (
    "DeviceInterfaceProfileTabView",
    "InterfaceProfileAssignmentBulkDeleteView",
    "InterfaceProfileAssignmentBulkEditView",
    "InterfaceProfileAssignmentBulkImportView",
    "InterfaceProfileAssignmentDeleteView",
    "InterfaceProfileAssignmentEditView",
    "InterfaceProfileAssignmentListView",
    "InterfaceProfileAssignmentMenuHTMXView",
    "InterfaceProfileAssignmentRemoveHTMXView",
    "InterfaceProfileAssignmentSetHTMXView",
    "InterfaceProfileAssignmentView",
    "InterfaceProfileBulkDeleteView",
    "InterfaceProfileBulkEditView",
    "InterfaceProfileBulkImportView",
    "InterfaceProfileDeleteView",
    "InterfaceProfileEditView",
    "InterfaceProfileListView",
    "InterfaceProfileSyncView",
    "InterfaceProfileView",
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
    "ProfileConfigTemplateDeleteView",
    "ProfileConfigTemplateEditView",
    "ProfileConfigTemplateListView",
    "ProfileConfigTemplateView",
)
