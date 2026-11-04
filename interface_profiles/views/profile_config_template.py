"""
ProfileConfigTemplate views for interface profiles.
"""

from core.object_actions import BulkSync
from netbox.object_actions import AddObject, BulkDelete, BulkEdit, BulkExport, BulkImport
from netbox.views import generic

from .. import filtersets, forms, models, tables


class ProfileConfigTemplateView(generic.ObjectView):
    queryset = models.ProfileConfigTemplate.objects.select_related(
        "interface_role", "platform", "device_type", "data_source", "data_file"
    ).prefetch_related("device_tags", "interface_tags")


class ProfileConfigTemplateListView(generic.ObjectListView):
    queryset = models.ProfileConfigTemplate.objects.select_related(
        "interface_role", "platform", "device_type", "data_source", "data_file"
    ).prefetch_related("device_tags", "interface_tags", "tags")
    table = tables.ProfileConfigTemplateTable
    filterset = filtersets.ProfileConfigTemplateFilterSet
    filterset_form = forms.ProfileConfigTemplateFilterSetForm
    actions = (AddObject, BulkImport, BulkExport, BulkSync, BulkEdit, BulkDelete)


class ProfileConfigTemplateEditView(generic.ObjectEditView):
    template_name = "interface_profiles/profileconfigtemplate_edit.html"

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


class ProfileConfigTemplateBulkSyncDataView(generic.BulkSyncDataView):
    queryset = models.ProfileConfigTemplate.objects.all()
