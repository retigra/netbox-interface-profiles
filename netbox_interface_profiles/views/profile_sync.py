"""
ProfileSync views for netbox interface profiles.
"""

from django.db.models import Count
from netbox.object_actions import BulkDelete, BulkExport, DeleteObject
from netbox.views import generic
from utilities.paginator import EnhancedPaginator, get_paginate_count
from utilities.views import ViewTab, register_model_view

from .. import models, tables
from ..services import describe_changes

SYNC_PERMISSIONS = ("dcim.change_interface", "netbox_interface_profiles.view_profilesync")


def _annotate_syncs(queryset):
    return queryset.select_related("interface_profile", "job__user").annotate(change_count=Count("changes"))


class ProfileSyncView(generic.ObjectView):
    """Show the interface changes a synchronization made, or would make in case of a dry run."""

    queryset = models.ProfileSync.objects.select_related("interface_profile", "job__user")
    actions = (DeleteObject,)

    def get_extra_context(self, request, instance):
        changes = instance.changes.select_related("interface")
        paginator = EnhancedPaginator(changes, get_paginate_count(request))
        page = paginator.get_page(request.GET.get("page"))

        return {
            "paginator": paginator,
            "page": page,
            "rows": describe_changes(page.object_list),
            "can_apply": (
                instance.dry_run
                and instance.is_completed
                and paginator.count > 0
                and request.user.has_perms(SYNC_PERMISSIONS)
            ),
        }


class ProfileSyncListView(generic.ObjectListView):
    queryset = _annotate_syncs(models.ProfileSync.objects.all())
    table = tables.ProfileSyncTable
    actions = (BulkExport, BulkDelete)


class ProfileSyncDeleteView(generic.ObjectDeleteView):
    queryset = models.ProfileSync.objects.all()


class ProfileSyncBulkDeleteView(generic.BulkDeleteView):
    queryset = _annotate_syncs(models.ProfileSync.objects.all())
    table = tables.ProfileSyncTable


@register_model_view(models.InterfaceProfile, name="syncs", path="syncs")
class InterfaceProfileSyncsTabView(generic.ObjectChildrenView):
    """Tab on the Interface Profile detail page listing its synchronizations."""

    queryset = models.InterfaceProfile.objects.all()
    child_model = models.ProfileSync
    table = tables.ProfileSyncTable
    actions = (BulkDelete,)
    tab = ViewTab(
        label="Synchronizations",
        badge=lambda obj: models.ProfileSync.objects.filter(interface_profile=obj).count(),
        permission="netbox_interface_profiles.view_profilesync",
    )

    def get_children(self, request, parent):
        return _annotate_syncs(
            models.ProfileSync.objects.restrict(request.user, "view").filter(interface_profile=parent)
        )
