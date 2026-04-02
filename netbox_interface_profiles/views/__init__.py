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
    InterfaceProfileView,
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
    "InterfaceProfileBulkDeleteView",
    "InterfaceProfileBulkEditView",
    "InterfaceProfileBulkImportView",
    "InterfaceProfileDeleteView",
    "InterfaceProfileEditView",
    "InterfaceProfileListView",
    "InterfaceProfileView",
    "ProfileConfigTemplateBulkDeleteView",
    "ProfileConfigTemplateBulkEditView",
    "ProfileConfigTemplateBulkImportView",
    "ProfileConfigTemplateDeleteView",
    "ProfileConfigTemplateEditView",
    "ProfileConfigTemplateListView",
    "ProfileConfigTemplateView",
)
