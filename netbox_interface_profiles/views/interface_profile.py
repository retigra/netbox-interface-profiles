"""
InterfaceProfile views for netbox interface profiles.
"""

from netbox.views import generic

from .. import filtersets, forms, models, tables


class InterfaceProfileView(generic.ObjectView):
    queryset = models.InterfaceProfile.objects.all()


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
