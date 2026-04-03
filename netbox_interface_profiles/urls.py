"""
URL patterns for netbox interface profiles.

For more information on URL routing, see:
https://docs.netbox.dev/en/stable/plugins/development/views/#url-registration

For Django URL patterns, see:
https://docs.djangoproject.com/en/stable/topics/http/urls/
"""

from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from . import models, views

urlpatterns = (
    # Interface Profiles
    path("interface-profiles/", views.InterfaceProfileListView.as_view(), name="interfaceprofile_list"),
    path("interface-profiles/add/", views.InterfaceProfileEditView.as_view(), name="interfaceprofile_add"),
    path(
        "interface-profiles/import/",
        views.InterfaceProfileBulkImportView.as_view(),
        name="interfaceprofile_import",
    ),
    path(
        "interface-profiles/edit/",
        views.InterfaceProfileBulkEditView.as_view(),
        name="interfaceprofile_bulk_edit",
    ),
    path(
        "interface-profiles/delete/",
        views.InterfaceProfileBulkDeleteView.as_view(),
        name="interfaceprofile_bulk_delete",
    ),
    path("interface-profiles/<int:pk>/", views.InterfaceProfileView.as_view(), name="interfaceprofile"),
    path(
        "interface-profiles/<int:pk>/edit/",
        views.InterfaceProfileEditView.as_view(),
        name="interfaceprofile_edit",
    ),
    path(
        "interface-profiles/<int:pk>/delete/",
        views.InterfaceProfileDeleteView.as_view(),
        name="interfaceprofile_delete",
    ),
    path(
        "interface-profiles/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="interfaceprofile_changelog",
        kwargs={"model": models.InterfaceProfile},
    ),
    path(
        "interface-profiles/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="interfaceprofile_journal",
        kwargs={"model": models.InterfaceProfile},
    ),
    # Profile Config Templates
    path(
        "profile-config-templates/",
        views.ProfileConfigTemplateListView.as_view(),
        name="profileconfigtemplate_list",
    ),
    path(
        "profile-config-templates/add/",
        views.ProfileConfigTemplateEditView.as_view(),
        name="profileconfigtemplate_add",
    ),
    path(
        "profile-config-templates/import/",
        views.ProfileConfigTemplateBulkImportView.as_view(),
        name="profileconfigtemplate_import",
    ),
    path(
        "profile-config-templates/edit/",
        views.ProfileConfigTemplateBulkEditView.as_view(),
        name="profileconfigtemplate_bulk_edit",
    ),
    path(
        "profile-config-templates/delete/",
        views.ProfileConfigTemplateBulkDeleteView.as_view(),
        name="profileconfigtemplate_bulk_delete",
    ),
    path(
        "profile-config-templates/<int:pk>/",
        views.ProfileConfigTemplateView.as_view(),
        name="profileconfigtemplate",
    ),
    path(
        "profile-config-templates/<int:pk>/edit/",
        views.ProfileConfigTemplateEditView.as_view(),
        name="profileconfigtemplate_edit",
    ),
    path(
        "profile-config-templates/<int:pk>/delete/",
        views.ProfileConfigTemplateDeleteView.as_view(),
        name="profileconfigtemplate_delete",
    ),
    path(
        "profile-config-templates/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="profileconfigtemplate_changelog",
        kwargs={"model": models.ProfileConfigTemplate},
    ),
    path(
        "profile-config-templates/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="profileconfigtemplate_journal",
        kwargs={"model": models.ProfileConfigTemplate},
    ),
    # Interface Profile Assignments
    path(
        "interface-profile-assignments/",
        views.InterfaceProfileAssignmentListView.as_view(),
        name="interfaceprofileassignment_list",
    ),
    path(
        "interface-profile-assignments/add/",
        views.InterfaceProfileAssignmentEditView.as_view(),
        name="interfaceprofileassignment_add",
    ),
    path(
        "interface-profile-assignments/import/",
        views.InterfaceProfileAssignmentBulkImportView.as_view(),
        name="interfaceprofileassignment_import",
    ),
    path(
        "interface-profile-assignments/edit/",
        views.InterfaceProfileAssignmentBulkEditView.as_view(),
        name="interfaceprofileassignment_bulk_edit",
    ),
    path(
        "interface-profile-assignments/delete/",
        views.InterfaceProfileAssignmentBulkDeleteView.as_view(),
        name="interfaceprofileassignment_bulk_delete",
    ),
    path(
        "interface-profile-assignments/<int:pk>/",
        views.InterfaceProfileAssignmentView.as_view(),
        name="interfaceprofileassignment",
    ),
    path(
        "interface-profile-assignments/<int:pk>/edit/",
        views.InterfaceProfileAssignmentEditView.as_view(),
        name="interfaceprofileassignment_edit",
    ),
    path(
        "interface-profile-assignments/<int:pk>/delete/",
        views.InterfaceProfileAssignmentDeleteView.as_view(),
        name="interfaceprofileassignment_delete",
    ),
    path(
        "interface-profile-assignments/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="interfaceprofileassignment_changelog",
        kwargs={"model": models.InterfaceProfileAssignment},
    ),
    path(
        "interface-profile-assignments/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="interfaceprofileassignment_journal",
        kwargs={"model": models.InterfaceProfileAssignment},
    ),
    # HTMX endpoints for device interface profile actions
    path(
        "interface-profile-assignments/htmx/interface/<int:interface_id>/menu/",
        views.InterfaceProfileAssignmentMenuHTMXView.as_view(),
        name="interfaceprofileassignment_htmx_menu",
    ),
    path(
        "interface-profile-assignments/htmx/interface/<int:interface_id>/set/<int:profile_id>/",
        views.InterfaceProfileAssignmentSetHTMXView.as_view(),
        name="interfaceprofileassignment_htmx_set",
    ),
    path(
        "interface-profile-assignments/htmx/interface/<int:interface_id>/remove/",
        views.InterfaceProfileAssignmentRemoveHTMXView.as_view(),
        name="interfaceprofileassignment_htmx_remove",
    ),
)
