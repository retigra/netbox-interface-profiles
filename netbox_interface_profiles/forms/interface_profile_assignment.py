"""
InterfaceProfileAssignment forms for netbox interface profiles.
"""

from dcim.models import Device, Interface
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

from ..models import InterfaceProfile, InterfaceProfileAssignment, ProfileGroup


def get_interface_profile_queryset(interface=None):
    """Get filtered queryset of InterfaceProfile based on interface's device role."""
    from django.db.models import Q

    queryset = InterfaceProfile.objects.all().order_by("name")

    if interface and interface.device:
        device = interface.device
        device_role = device.role

        if device_role:
            # Profiles with this device_role OR profiles with no device_role restriction
            queryset = queryset.filter(Q(device_roles__isnull=True) | Q(device_roles=device_role)).distinct()

    return queryset


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter profiles based on the interface's device role if editing existing assignment
        if self.instance.interface_id:
            self.fields["interface_profile"].queryset = get_interface_profile_queryset(self.instance.interface)


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

    def __init__(self, device=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter profiles based on device role if device is provided
        if device:
            self.fields["interface_profile"].queryset = InterfaceProfile.objects.filter(
                device_roles__isnull=True
            ) | InterfaceProfile.objects.filter(device_roles=device.role)
            self.fields["interface_profile"].queryset = (
                self.fields["interface_profile"].queryset.distinct().order_by("name")
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
    interface_profile_group_id = DynamicModelMultipleChoiceField(
        queryset=ProfileGroup.objects.all(),
        required=False,
        null_option="None",
        label=_("Profile Group"),
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_("Device"),
    )
