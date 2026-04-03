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
    "ProfileConfigTemplateBulkEditForm",
    "ProfileConfigTemplateFilterSetForm",
    "ProfileConfigTemplateForm",
    "ProfileConfigTemplateImportForm",
)
