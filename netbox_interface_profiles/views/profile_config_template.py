"""
ProfileConfigTemplate views for netbox interface profiles.
"""

from netbox.views import generic

from .. import filtersets, forms, models, tables


class ProfileConfigTemplateView(generic.ObjectView):
    queryset = models.ProfileConfigTemplate.objects.select_related("interface_template", "platform", "device_type")


class ProfileConfigTemplateListView(generic.ObjectListView):
    queryset = models.ProfileConfigTemplate.objects.select_related("interface_template", "platform", "device_type")
    table = tables.ProfileConfigTemplateTable
    filterset = filtersets.ProfileConfigTemplateFilterSet
    filterset_form = forms.ProfileConfigTemplateFilterSetForm


class ProfileConfigTemplateEditView(generic.ObjectEditView):
    template_name = "netbox_interface_profiles/profileconfigtemplate_edit.html"

    queryset = models.ProfileConfigTemplate.objects.all()
    form = forms.ProfileConfigTemplateForm


class ProfileConfigTemplateDeleteView(generic.ObjectDeleteView):
    queryset = models.ProfileConfigTemplate.objects.all()


class ProfileConfigTemplateBulkImportView(generic.BulkImportView):
    queryset = models.ProfileConfigTemplate.objects.all()
    model_form = forms.ProfileConfigTemplateImportForm
    table = tables.ProfileConfigTemplateTable


class ProfileConfigTemplateBulkEditView(generic.BulkEditView):
    queryset = models.ProfileConfigTemplate.objects.all()
    filterset = filtersets.ProfileConfigTemplateFilterSet
    table = tables.ProfileConfigTemplateTable
    form = forms.ProfileConfigTemplateBulkEditForm


class ProfileConfigTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ProfileConfigTemplate.objects.all()
    filterset = filtersets.ProfileConfigTemplateFilterSet
    table = tables.ProfileConfigTemplateTable
