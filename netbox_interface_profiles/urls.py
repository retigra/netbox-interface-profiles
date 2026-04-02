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
)
