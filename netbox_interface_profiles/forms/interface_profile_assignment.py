"""
InterfaceProfileAssignment forms for netbox interface profiles.
"""

from dcim.models import Interface
from django import forms
from django.utils.translation import gettext_lazy as _
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet

from ..models import InterfaceProfile, InterfaceProfileAssignment


class InterfaceProfileAssignmentForm(NetBoxModelForm):
    """Create / Edit form for InterfaceProfileAssignment."""

    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        label=_("Interface"),
    )
    interface_profile = DynamicModelChoiceField(
        queryset=InterfaceProfile.objects.all(),
        label=_("Interface Profile"),
    )

    fieldsets = (FieldSet("interface", "interface_profile", "tags", name=_("Assignment")),)

    class Meta:
        model = InterfaceProfileAssignment
        fields = ("interface", "interface_profile", "tags")


class InterfaceProfileAssignmentImportForm(NetBoxModelImportForm):
    """CSV import form for InterfaceProfileAssignment."""

    class Meta:
        model = InterfaceProfileAssignment
        fields = ("interface", "interface_profile")


class InterfaceProfileAssignmentBulkEditForm(NetBoxModelBulkEditForm):
    """Bulk edit form for InterfaceProfileAssignment."""

    model = InterfaceProfileAssignment

    pk = forms.ModelMultipleChoiceField(
        queryset=InterfaceProfileAssignment.objects.all(),
        widget=forms.MultipleHiddenInput(),
    )
    interface_profile = DynamicModelChoiceField(
        queryset=InterfaceProfile.objects.all(),
        required=False,
        label=_("Interface Profile"),
    )

    class Meta:
        nullable_fields = ()


class DeviceBulkAssignProfileForm(forms.Form):
    """Form for bulk-assigning an Interface Profile to selected interfaces on the Device tab."""

    interface_profile = DynamicModelChoiceField(
        queryset=InterfaceProfile.objects.all(),
        label=_("Interface Profile"),
        required=False,
    )


class InterfaceProfileAssignmentFilterSetForm(NetBoxModelFilterSetForm):
    """Filter form for the InterfaceProfileAssignment list view."""

    model = InterfaceProfileAssignment

    interface_id = DynamicModelMultipleChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_("Interface"),
    )
    interface_profile_id = DynamicModelMultipleChoiceField(
        queryset=InterfaceProfile.objects.all(),
        required=False,
        label=_("Interface Profile"),
    )
