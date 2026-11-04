"""
RoleSync views for interface profiles.
"""

from django.db.models import Count
from netbox.object_actions import BulkDelete, BulkExport, DeleteObject
from netbox.views import generic
from utilities.paginator import EnhancedPaginator, get_paginate_count
from utilities.views import ViewTab, register_model_view

from .. import models, tables
from ..services import describe_changes

SYNC_PERMISSIONS = ("dcim.change_interface", "interface_profiles.view_rolesync")


def _annotate_syncs(queryset):
    return queryset.select_related("interface_role", "job__user").annotate(change_count=Count("changes"))


class RoleSyncView(generic.ObjectView):
    """Show the interface changes a synchronization made, or would make in case of a dry run."""

    queryset = models.RoleSync.objects.select_related("interface_role", "job__user")
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


class RoleSyncListView(generic.ObjectListView):
    queryset = _annotate_syncs(models.RoleSync.objects.all())
    table = tables.RoleSyncTable
    actions = (BulkExport, BulkDelete)


class RoleSyncDeleteView(generic.ObjectDeleteView):
    queryset = models.RoleSync.objects.all()


class RoleSyncBulkDeleteView(generic.BulkDeleteView):
    queryset = _annotate_syncs(models.RoleSync.objects.all())
    table = tables.RoleSyncTable


@register_model_view(models.InterfaceRole, name="syncs", path="syncs")
class InterfaceRoleSyncsTabView(generic.ObjectChildrenView):
    """Tab on the Interface Role detail page listing its synchronizations."""

    queryset = models.InterfaceRole.objects.all()
    child_model = models.RoleSync
    table = tables.RoleSyncTable
    actions = (BulkDelete,)
    tab = ViewTab(
        label="Synchronizations",
        badge=lambda obj: models.RoleSync.objects.filter(interface_role=obj).count(),
        permission="interface_profiles.view_rolesync",
    )

    def get_children(self, request, parent):
        return _annotate_syncs(models.RoleSync.objects.restrict(request.user, "view").filter(interface_role=parent))
