"""
InterfaceProfile views for netbox interface profiles.
"""

from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from netbox.views import generic

from .. import filtersets, forms, models, tables
from ..jobs import SyncInterfaceProfileJob


class InterfaceProfileView(generic.ObjectView):
    queryset = models.InterfaceProfile.objects.all()

    def get_extra_context(self, request, instance):
        """Provide related template querysets for the detail page."""
        related_interface_templates = models.InterfaceTemplate.objects.restrict(request.user, "view").filter(
            interface_profile=instance
        )
        related_config_templates = models.ProfileConfigTemplate.objects.restrict(request.user, "view").filter(
            interface_profile=instance
        )

        return {
            "related_interface_templates": related_interface_templates.select_related("site_group").order_by(
                "name",
                "pk",
            ),
            "related_config_templates": related_config_templates.select_related(
                "platform",
                "device_type",
            ).order_by("name", "pk"),
        }


class InterfaceProfileListView(generic.ObjectListView):
    queryset = models.InterfaceProfile.objects.all()
    table = tables.InterfaceProfileTable
    filterset = filtersets.InterfaceProfileFilterSet
    filterset_form = forms.InterfaceProfileFilterSetForm


class InterfaceProfileEditView(generic.ObjectEditView):
    queryset = models.InterfaceProfile.objects.all()
    form = forms.InterfaceProfileForm


class InterfaceProfileDeleteView(generic.ObjectDeleteView):
    queryset = models.InterfaceProfile.objects.all()


class InterfaceProfileBulkImportView(generic.BulkImportView):
    queryset = models.InterfaceProfile.objects.all()
    model_form = forms.InterfaceProfileImportForm
    table = tables.InterfaceProfileTable


class InterfaceProfileBulkEditView(generic.BulkEditView):
    queryset = models.InterfaceProfile.objects.all()
    filterset = filtersets.InterfaceProfileFilterSet
    table = tables.InterfaceProfileTable
    form = forms.InterfaceProfileBulkEditForm


class InterfaceProfileBulkDeleteView(generic.BulkDeleteView):
    queryset = models.InterfaceProfile.objects.all()
    filterset = filtersets.InterfaceProfileFilterSet
    table = tables.InterfaceProfileTable


class InterfaceProfileSyncView(View):
    """Queue a background job to synchronize all interfaces assigned to a profile."""

    def _has_permission(self, request) -> bool:
        return request.user.has_perm("dcim.change_interface")

    def get(self, request, pk: int):
        if not self._has_permission(request):
            return HttpResponseForbidden()

        profile = get_object_or_404(models.InterfaceProfile.objects.all(), pk=pk)
        form = forms.InterfaceProfileSyncForm()
        return render(
            request,
            "netbox_interface_profiles/interfaceprofile_sync.html",
            {
                "object": profile,
                "form": form,
            },
        )

    def post(self, request, pk: int):
        if not self._has_permission(request):
            return HttpResponseForbidden()

        profile = get_object_or_404(models.InterfaceProfile.objects.all(), pk=pk)
        form = forms.InterfaceProfileSyncForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                "netbox_interface_profiles/interfaceprofile_sync.html",
                {
                    "object": profile,
                    "form": form,
                },
            )

        dry_run = form.cleaned_data.get("dry_run", True)
        job = SyncInterfaceProfileJob.enqueue(
            user=request.user,
            dry_run=dry_run,
            profile_id=profile.pk,
        )

        mode = _("dry-run") if dry_run else _("commit")
        messages.success(
            request,
            _("Queued synchronization job #{id} for profile {profile} ({mode}).").format(
                id=job.pk,
                profile=profile,
                mode=mode,
            ),
        )

        return redirect(job.get_absolute_url())
