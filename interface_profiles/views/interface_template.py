"""
InterfaceTemplate views for interface profiles.
"""

from netbox.views import generic

from .. import filtersets, forms, models, tables


class InterfaceTemplateView(generic.ObjectView):
    """Detail view for InterfaceTemplate."""

    queryset = models.InterfaceTemplate.objects.select_related(
        "interface_role",
        "scope_type",
    )


class InterfaceTemplateListView(generic.ObjectListView):
    """List view for InterfaceTemplate."""

    queryset = models.InterfaceTemplate.objects.select_related(
        "interface_role",
        "scope_type",
    )
    table = tables.InterfaceTemplateTable
    filterset = filtersets.InterfaceTemplateFilterSet
    filterset_form = forms.InterfaceTemplateFilterSetForm


class InterfaceTemplateEditView(generic.ObjectEditView):
    """Create/Edit view for InterfaceTemplate."""

    queryset = models.InterfaceTemplate.objects.all()
    form = forms.InterfaceTemplateForm


class InterfaceTemplateDeleteView(generic.ObjectDeleteView):
    """Delete view for InterfaceTemplate."""

    queryset = models.InterfaceTemplate.objects.all()


class InterfaceTemplateBulkImportView(generic.BulkImportView):
    """Bulk import view for InterfaceTemplate."""

    queryset = models.InterfaceTemplate.objects.all()
    model_form = forms.InterfaceTemplateImportForm
    table = tables.InterfaceTemplateTable


class InterfaceTemplateBulkEditView(generic.BulkEditView):
    """Bulk edit view for InterfaceTemplate."""

    queryset = models.InterfaceTemplate.objects.all()
    filterset = filtersets.InterfaceTemplateFilterSet
    table = tables.InterfaceTemplateTable
    form = forms.InterfaceTemplateBulkEditForm


class InterfaceTemplateBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for InterfaceTemplate."""

    queryset = models.InterfaceTemplate.objects.all()
    filterset = filtersets.InterfaceTemplateFilterSet
    table = tables.InterfaceTemplateTable
