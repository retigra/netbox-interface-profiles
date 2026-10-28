"""
URL patterns for netbox interface profiles.

For more information on URL routing, see:
https://docs.netbox.dev/en/stable/plugins/development/views/#url-registration

For Django URL patterns, see:
https://docs.djangoproject.com/en/stable/topics/http/urls/
"""

from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJobsView, ObjectJournalView

from . import models, views

urlpatterns = (
    # Role Groups
    path("role-groups/", views.RoleGroupListView.as_view(), name="rolegroup_list"),
    path("role-groups/add/", views.RoleGroupEditView.as_view(), name="rolegroup_add"),
    path("role-groups/import/", views.RoleGroupBulkImportView.as_view(), name="rolegroup_import"),
    path("role-groups/edit/", views.RoleGroupBulkEditView.as_view(), name="rolegroup_bulk_edit"),
    path("role-groups/delete/", views.RoleGroupBulkDeleteView.as_view(), name="rolegroup_bulk_delete"),
    path("role-groups/<int:pk>/", views.RoleGroupView.as_view(), name="rolegroup"),
    path("role-groups/<int:pk>/edit/", views.RoleGroupEditView.as_view(), name="rolegroup_edit"),
    path("role-groups/<int:pk>/delete/", views.RoleGroupDeleteView.as_view(), name="rolegroup_delete"),
    path(
        "role-groups/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="rolegroup_changelog",
        kwargs={"model": models.RoleGroup},
    ),
    path(
        "role-groups/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="rolegroup_journal",
        kwargs={"model": models.RoleGroup},
    ),
    # Interface Roles
    path("interface-roles/", views.InterfaceRoleListView.as_view(), name="interfacerole_list"),
    path("interface-roles/add/", views.InterfaceRoleEditView.as_view(), name="interfacerole_add"),
    path(
        "interface-roles/import/",
        views.InterfaceRoleBulkImportView.as_view(),
        name="interfacerole_import",
    ),
    path(
        "interface-roles/edit/",
        views.InterfaceRoleBulkEditView.as_view(),
        name="interfacerole_bulk_edit",
    ),
    path(
        "interface-roles/delete/",
        views.InterfaceRoleBulkDeleteView.as_view(),
        name="interfacerole_bulk_delete",
    ),
    path("interface-roles/<int:pk>/", views.InterfaceRoleView.as_view(), name="interfacerole"),
    path(
        "interface-roles/<int:pk>/interfaces/",
        views.InterfaceRoleInterfacesTabView.as_view(),
        name="interfacerole_interfaces",
    ),
    path(
        "interface-roles/<int:pk>/sync/",
        views.InterfaceRoleSyncView.as_view(),
        name="interfacerole_sync",
    ),
    path(
        "interface-roles/<int:pk>/syncs/",
        views.InterfaceRoleSyncsTabView.as_view(),
        name="interfacerole_syncs",
    ),
    path(
        "interface-roles/<int:pk>/edit/",
        views.InterfaceRoleEditView.as_view(),
        name="interfacerole_edit",
    ),
    path(
        "interface-roles/<int:pk>/delete/",
        views.InterfaceRoleDeleteView.as_view(),
        name="interfacerole_delete",
    ),
    path(
        "interface-roles/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="interfacerole_changelog",
        kwargs={"model": models.InterfaceRole},
    ),
    path(
        "interface-roles/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="interfacerole_journal",
        kwargs={"model": models.InterfaceRole},
    ),
    path(
        "interface-roles/<int:pk>/jobs/",
        ObjectJobsView.as_view(),
        name="interfacerole_jobs",
        kwargs={"model": models.InterfaceRole},
    ),
    # Role Synchronizations
    path("role-syncs/", views.RoleSyncListView.as_view(), name="rolesync_list"),
    path("role-syncs/delete/", views.RoleSyncBulkDeleteView.as_view(), name="rolesync_bulk_delete"),
    path("role-syncs/<int:pk>/", views.RoleSyncView.as_view(), name="rolesync"),
    path("role-syncs/<int:pk>/delete/", views.RoleSyncDeleteView.as_view(), name="rolesync_delete"),
    # Interface Templates
    path("interface-templates/", views.InterfaceTemplateListView.as_view(), name="interfacetemplate_list"),
    path("interface-templates/add/", views.InterfaceTemplateEditView.as_view(), name="interfacetemplate_add"),
    path(
        "interface-templates/import/",
        views.InterfaceTemplateBulkImportView.as_view(),
        name="interfacetemplate_import",
    ),
    path(
        "interface-templates/edit/",
        views.InterfaceTemplateBulkEditView.as_view(),
        name="interfacetemplate_bulk_edit",
    ),
    path(
        "interface-templates/delete/",
        views.InterfaceTemplateBulkDeleteView.as_view(),
        name="interfacetemplate_bulk_delete",
    ),
    path("interface-templates/<int:pk>/", views.InterfaceTemplateView.as_view(), name="interfacetemplate"),
    path(
        "interface-templates/<int:pk>/edit/",
        views.InterfaceTemplateEditView.as_view(),
        name="interfacetemplate_edit",
    ),
    path(
        "interface-templates/<int:pk>/delete/",
        views.InterfaceTemplateDeleteView.as_view(),
        name="interfacetemplate_delete",
    ),
    path(
        "interface-templates/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="interfacetemplate_changelog",
        kwargs={"model": models.InterfaceTemplate},
    ),
    path(
        "interface-templates/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="interfacetemplate_journal",
        kwargs={"model": models.InterfaceTemplate},
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
    # Interface Role Assignments
    path(
        "interface-role-assignments/",
        views.InterfaceRoleAssignmentListView.as_view(),
        name="interfaceroleassignment_list",
    ),
    path(
        "interface-role-assignments/add/",
        views.InterfaceRoleAssignmentEditView.as_view(),
        name="interfaceroleassignment_add",
    ),
    path(
        "interface-role-assignments/import/",
        views.InterfaceRoleAssignmentBulkImportView.as_view(),
        name="interfaceroleassignment_import",
    ),
    path(
        "interface-role-assignments/edit/",
        views.InterfaceRoleAssignmentBulkEditView.as_view(),
        name="interfaceroleassignment_bulk_edit",
    ),
    path(
        "interface-role-assignments/delete/",
        views.InterfaceRoleAssignmentBulkDeleteView.as_view(),
        name="interfaceroleassignment_bulk_delete",
    ),
    path(
        "interface-role-assignments/<int:pk>/",
        views.InterfaceRoleAssignmentView.as_view(),
        name="interfaceroleassignment",
    ),
    path(
        "interface-role-assignments/<int:pk>/edit/",
        views.InterfaceRoleAssignmentEditView.as_view(),
        name="interfaceroleassignment_edit",
    ),
    path(
        "interface-role-assignments/<int:pk>/delete/",
        views.InterfaceRoleAssignmentDeleteView.as_view(),
        name="interfaceroleassignment_delete",
    ),
    path(
        "interface-role-assignments/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="interfaceroleassignment_changelog",
        kwargs={"model": models.InterfaceRoleAssignment},
    ),
    path(
        "interface-role-assignments/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="interfaceroleassignment_journal",
        kwargs={"model": models.InterfaceRoleAssignment},
    ),
    # HTMX endpoints for device interface role actions
    path(
        "interface-role-assignments/htmx/interface/<int:interface_id>/menu/",
        views.InterfaceRoleAssignmentMenuHTMXView.as_view(),
        name="interfaceroleassignment_htmx_menu",
    ),
    path(
        "interface-role-assignments/htmx/interface/<int:interface_id>/set/<int:role_id>/",
        views.InterfaceRoleAssignmentSetHTMXView.as_view(),
        name="interfaceroleassignment_htmx_set",
    ),
    path(
        "interface-role-assignments/htmx/interface/<int:interface_id>/remove/",
        views.InterfaceRoleAssignmentRemoveHTMXView.as_view(),
        name="interfaceroleassignment_htmx_remove",
    ),
)
