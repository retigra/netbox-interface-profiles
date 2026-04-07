"""
Forms for netbox interface profiles.

For more information on NetBox forms, see:
https://docs.netbox.dev/en/stable/plugins/development/forms/
"""

from .interface_profile import (
    InterfaceProfileBulkEditForm,
    InterfaceProfileFilterSetForm,
    InterfaceProfileForm,
    InterfaceProfileImportForm,
)
from .interface_profile_assignment import (
    DeviceBulkAssignProfileForm,
    InterfaceProfileAssignmentBulkEditForm,
    InterfaceProfileAssignmentFilterSetForm,
    InterfaceProfileAssignmentForm,
    InterfaceProfileAssignmentImportForm,
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

__all__ = (
    "DeviceBulkAssignProfileForm",
    "InterfaceProfileAssignmentBulkEditForm",
    "InterfaceProfileAssignmentFilterSetForm",
    "InterfaceProfileAssignmentForm",
    "InterfaceProfileAssignmentImportForm",
    "InterfaceProfileBulkEditForm",
    "InterfaceProfileFilterSetForm",
    "InterfaceProfileForm",
    "InterfaceProfileImportForm",
    "InterfaceTemplateBulkEditForm",
    "InterfaceTemplateFilterSetForm",
    "InterfaceTemplateForm",
    "InterfaceTemplateImportForm",
    "ProfileConfigTemplateBulkEditForm",
    "ProfileConfigTemplateFilterSetForm",
    "ProfileConfigTemplateForm",
    "ProfileConfigTemplateImportForm",
)
