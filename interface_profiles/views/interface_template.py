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
    ).prefetch_related("scope_sites", "scope_site_groups")
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

    def _update_objects(self, form, request):
        # The scope is not a model field, so BulkEditView cannot nullify it: InterfaceTemplateBulkEditForm does
        nullified = request.POST.getlist("_nullify")
        self._nullify_scope = "scope" in nullified
        if self._nullify_scope:
            request.POST = request.POST.copy()
            request.POST.setlist("_nullify", [name for name in nullified if name != "scope"])
        return super()._update_objects(form, request)

    def pre_save_operations(self, form, obj):
        # Validated by InterfaceTemplate.clean() and saved by post_save_operations()
        obj._scope_values = {}
        if scope := form.get_scope(self._nullify_scope):
            obj.scope_type, obj._scope_values = scope
            obj._m2m_values.update(obj._scope_values)

    def post_save_operations(self, form, obj):
        for relation, scopes in obj._scope_values.items():
            getattr(obj, relation).set(scopes)


class InterfaceTemplateBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for InterfaceTemplate."""

    queryset = models.InterfaceTemplate.objects.all()
    filterset = filtersets.InterfaceTemplateFilterSet
    table = tables.InterfaceTemplateTable
