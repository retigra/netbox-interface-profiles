"""
InterfaceProfile forms for netbox interface profiles.
"""

from django import forms
from django.utils.translation.trans_null import _
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from utilities.forms.rendering import FieldSet

from ..models import InterfaceProfile


class InterfaceProfileForm(NetBoxModelForm):
    """Create / Edit form for InterfaceProfile."""

    fieldsets = (FieldSet("name", "description", "tags", name=_("Interface Profile")),)

    class Meta:
        model = InterfaceProfile
        fields = ("name", "description", "tags")


class InterfaceProfileImportForm(NetBoxModelImportForm):
    """CSV import form for InterfaceProfile."""

    class Meta:
        model = InterfaceProfile
        fields = ("name", "description")


class InterfaceProfileBulkEditForm(NetBoxModelBulkEditForm):
    """Bulk edit form for InterfaceProfile."""

    model = InterfaceProfile

    pk = forms.ModelMultipleChoiceField(
        queryset=InterfaceProfile.objects.all(),
        widget=forms.MultipleHiddenInput(),
    )
    description = forms.CharField(max_length=200, required=False)

    class Meta:
        nullable_fields = ("description",)


class InterfaceProfileFilterSetForm(NetBoxModelFilterSetForm):
    """Filter form for the InterfaceProfile list view."""

    model = InterfaceProfile
    name = forms.CharField(required=False)
    description = forms.CharField(required=False)
