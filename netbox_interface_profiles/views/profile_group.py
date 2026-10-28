"""
ProfileGroup views for netbox interface profiles.
"""

from extras.ui.panels import CustomFieldsPanel, TagsPanel
from netbox.ui import layout
from netbox.ui.panels import CommentsPanel, ObjectsTablePanel, OrganizationalObjectPanel, RelatedObjectsPanel
from netbox.views import generic
from utilities.query import count_related
from utilities.views import GetRelatedModelsMixin

from .. import filtersets, forms, models, tables


class ProfileGroupView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = models.ProfileGroup.objects.all()
    template_name = "generic/object.html"
    layout = layout.SimpleLayout(
        left_panels=[OrganizationalObjectPanel(), TagsPanel()],
        right_panels=[RelatedObjectsPanel(), CustomFieldsPanel(), CommentsPanel()],
        bottom_panels=[
            ObjectsTablePanel(
                model="netbox_interface_profiles.InterfaceProfile",
                filters={"group_id": lambda ctx: ctx["object"].pk},
                exclude_columns=["group"],
            ),
        ],
    )

    def get_extra_context(self, request, instance):
        return {
            "related_models": self.get_related_models(request, instance),
        }


class ProfileGroupListView(generic.ObjectListView):
    queryset = models.ProfileGroup.objects.annotate(
        interface_profile_count=count_related(models.InterfaceProfile, "group"),
    )
    table = tables.ProfileGroupTable
    filterset = filtersets.ProfileGroupFilterSet
    filterset_form = forms.ProfileGroupFilterSetForm


class ProfileGroupEditView(generic.ObjectEditView):
    queryset = models.ProfileGroup.objects.all()
    form = forms.ProfileGroupForm


class ProfileGroupDeleteView(generic.ObjectDeleteView):
    queryset = models.ProfileGroup.objects.all()


class ProfileGroupBulkImportView(generic.BulkImportView):
    queryset = models.ProfileGroup.objects.all()
    model_form = forms.ProfileGroupImportForm


class ProfileGroupBulkEditView(generic.BulkEditView):
    queryset = models.ProfileGroup.objects.annotate(
        interface_profile_count=count_related(models.InterfaceProfile, "group"),
    )
    filterset = filtersets.ProfileGroupFilterSet
    table = tables.ProfileGroupTable
    form = forms.ProfileGroupBulkEditForm


class ProfileGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ProfileGroup.objects.annotate(
        interface_profile_count=count_related(models.InterfaceProfile, "group"),
    )
    filterset = filtersets.ProfileGroupFilterSet
    table = tables.ProfileGroupTable
