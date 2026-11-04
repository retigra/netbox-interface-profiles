"""
RoleGroup views for interface profiles.
"""

from extras.ui.panels import CustomFieldsPanel, TagsPanel
from netbox.ui import layout
from netbox.ui.panels import CommentsPanel, ObjectsTablePanel, OrganizationalObjectPanel, RelatedObjectsPanel
from netbox.views import generic
from utilities.query import count_related
from utilities.views import GetRelatedModelsMixin

from .. import filtersets, forms, models, tables


class RoleGroupView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = models.RoleGroup.objects.all()
    template_name = "generic/object.html"
    layout = layout.SimpleLayout(
        left_panels=[OrganizationalObjectPanel(), TagsPanel()],
        right_panels=[RelatedObjectsPanel(), CustomFieldsPanel(), CommentsPanel()],
        bottom_panels=[
            ObjectsTablePanel(
                model="interface_profiles.InterfaceRole",
                filters={"group_id": lambda ctx: ctx["object"].pk},
                exclude_columns=["group"],
            ),
        ],
    )

    def get_extra_context(self, request, instance):
        return {
            "related_models": self.get_related_models(request, instance),
        }


class RoleGroupListView(generic.ObjectListView):
    queryset = models.RoleGroup.objects.annotate(
        interface_role_count=count_related(models.InterfaceRole, "group"),
    )
    table = tables.RoleGroupTable
    filterset = filtersets.RoleGroupFilterSet
    filterset_form = forms.RoleGroupFilterSetForm


class RoleGroupEditView(generic.ObjectEditView):
    queryset = models.RoleGroup.objects.all()
    form = forms.RoleGroupForm


class RoleGroupDeleteView(generic.ObjectDeleteView):
    queryset = models.RoleGroup.objects.all()


class RoleGroupBulkImportView(generic.BulkImportView):
    queryset = models.RoleGroup.objects.all()
    model_form = forms.RoleGroupImportForm


class RoleGroupBulkEditView(generic.BulkEditView):
    queryset = models.RoleGroup.objects.annotate(
        interface_role_count=count_related(models.InterfaceRole, "group"),
    )
    filterset = filtersets.RoleGroupFilterSet
    table = tables.RoleGroupTable
    form = forms.RoleGroupBulkEditForm


class RoleGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = models.RoleGroup.objects.annotate(
        interface_role_count=count_related(models.InterfaceRole, "group"),
    )
    filterset = filtersets.RoleGroupFilterSet
    table = tables.RoleGroupTable
