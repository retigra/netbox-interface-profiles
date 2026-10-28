"""
InterfaceRole views for netbox interface profiles.
"""

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from netbox.object_actions import BulkDelete, BulkEdit, DeleteObject, EditObject
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from .. import filtersets, forms, models, tables
from ..jobs import SyncInterfaceRoleJob
from .role_sync import SYNC_PERMISSIONS


class InterfaceRoleView(generic.ObjectView):
    queryset = models.InterfaceRole.objects.all()


class InterfaceRoleListView(generic.ObjectListView):
    queryset = models.InterfaceRole.objects.all()
    table = tables.InterfaceRoleTable
    filterset = filtersets.InterfaceRoleFilterSet
    filterset_form = forms.InterfaceRoleFilterSetForm


class InterfaceRoleEditView(generic.ObjectEditView):
    queryset = models.InterfaceRole.objects.all()
    form = forms.InterfaceRoleForm


class InterfaceRoleDeleteView(generic.ObjectDeleteView):
    queryset = models.InterfaceRole.objects.all()


class InterfaceRoleBulkImportView(generic.BulkImportView):
    queryset = models.InterfaceRole.objects.all()
    model_form = forms.InterfaceRoleImportForm
    table = tables.InterfaceRoleTable


class InterfaceRoleBulkEditView(generic.BulkEditView):
    queryset = models.InterfaceRole.objects.all()
    filterset = filtersets.InterfaceRoleFilterSet
    table = tables.InterfaceRoleTable
    form = forms.InterfaceRoleBulkEditForm


class InterfaceRoleBulkDeleteView(generic.BulkDeleteView):
    queryset = models.InterfaceRole.objects.all()
    filterset = filtersets.InterfaceRoleFilterSet
    table = tables.InterfaceRoleTable


@register_model_view(models.InterfaceRole, name="interfaces", path="interfaces")
class InterfaceRoleInterfacesTabView(generic.ObjectChildrenView):
    """Tab on the Interface Role detail page listing assigned interfaces."""

    queryset = models.InterfaceRole.objects.all()
    child_model = models.InterfaceRoleAssignment
    table = tables.InterfaceRoleAssignmentTable
    filterset = filtersets.InterfaceRoleAssignmentFilterSet
    filterset_form = forms.InterfaceRoleAssignmentFilterSetForm
    actions = (EditObject, DeleteObject, BulkEdit, BulkDelete)
    tab = ViewTab(
        label="Interfaces",
        badge=lambda obj: models.InterfaceRoleAssignment.objects.filter(interface_role=obj).count(),
        permission="netbox_interface_profiles.view_interfaceroleassignment",
    )

    def get_children(self, request, parent):
        return (
            models.InterfaceRoleAssignment.objects.restrict(request.user, "view")
            .filter(interface_role=parent)
            .select_related("interface__device", "interface_role")
            .order_by("interface__device__name", "interface__name", "pk")
        )


class InterfaceRoleSyncView(View):
    """Queue a background job to synchronize all interfaces assigned to a role."""

    def _has_permission(self, request) -> bool:
        return request.user.has_perms(SYNC_PERMISSIONS)

    def get(self, request, pk: int):
        if not self._has_permission(request):
            return HttpResponseForbidden()

        role = get_object_or_404(models.InterfaceRole.objects.all(), pk=pk)
        form = forms.InterfaceRoleSyncForm()
        return render(
            request,
            "netbox_interface_profiles/interfacerole_sync.html",
            {
                "object": role,
                "form": form,
            },
        )

    def post(self, request, pk: int):
        if not self._has_permission(request):
            return HttpResponseForbidden()

        role = get_object_or_404(models.InterfaceRole.objects.all(), pk=pk)
        form = forms.InterfaceRoleSyncForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                "netbox_interface_profiles/interfacerole_sync.html",
                {
                    "object": role,
                    "form": form,
                },
            )

        dry_run = form.cleaned_data.get("dry_run", True)

        # Create the job and its sync record together, so the worker never picks up a job without one
        with transaction.atomic():
            job = SyncInterfaceRoleJob.enqueue(instance=role, user=request.user)
            sync = models.RoleSync.objects.create(interface_role=role, job=job, dry_run=dry_run)

        if dry_run:
            message = _("Started a dry run for role {role}. No interfaces will be changed.")
        else:
            message = _("Started synchronizing role {role}.")
        messages.success(request, message.format(role=role))

        return redirect(sync.get_absolute_url())
