"""
InterfaceRoleAssignment forms for interface profiles.
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

from ..models import InterfaceRole, InterfaceRoleAssignment, RoleGroup


def get_interface_role_queryset(interface=None):
    """Get filtered queryset of InterfaceRole based on interface's device role."""
    from django.db.models import Q

    queryset = InterfaceRole.objects.all().order_by("name")

    if interface and interface.device:
        device = interface.device
        device_role = device.role

        if device_role:
            # Roles with this device_role OR roles with no device_role restriction
            queryset = queryset.filter(Q(device_roles__isnull=True) | Q(device_roles=device_role)).distinct()

    return queryset


class InterfaceRoleAssignmentForm(NetBoxModelForm):
    """Create / Edit form for InterfaceRoleAssignment."""

    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        label=_("Interface"),
    )
    interface_role = DynamicModelChoiceField(
        queryset=InterfaceRole.objects.all(),
        label=_("Interface Role"),
    )

    fieldsets = (FieldSet("interface", "interface_role", "tags", name=_("Assignment")),)

    class Meta:
        model = InterfaceRoleAssignment
        fields = ("interface", "interface_role", "tags")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter roles based on the interface's device role if editing existing assignment
        if self.instance.interface_id:
            self.fields["interface_role"].queryset = get_interface_role_queryset(self.instance.interface)


class InterfaceRoleAssignmentImportForm(NetBoxModelImportForm):
    """CSV import form for InterfaceRoleAssignment."""

    class Meta:
        model = InterfaceRoleAssignment
        fields = ("interface", "interface_role")


class InterfaceRoleAssignmentBulkEditForm(NetBoxModelBulkEditForm):
    """Bulk edit form for InterfaceRoleAssignment."""

    model = InterfaceRoleAssignment

    pk = forms.ModelMultipleChoiceField(
        queryset=InterfaceRoleAssignment.objects.all(),
        widget=forms.MultipleHiddenInput(),
    )
    interface_role = DynamicModelChoiceField(
        queryset=InterfaceRole.objects.all(),
        required=False,
        label=_("Interface Role"),
    )

    class Meta:
        nullable_fields = ()


class DeviceBulkAssignRoleForm(forms.Form):
    """Form for bulk-assigning an Interface Role to selected interfaces on the Device tab."""

    interface_role = DynamicModelChoiceField(
        queryset=InterfaceRole.objects.all(),
        label=_("Interface Role"),
        required=False,
    )

    def __init__(self, device=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter roles based on device role if device is provided
        if device:
            self.fields["interface_role"].queryset = InterfaceRole.objects.filter(
                device_roles__isnull=True
            ) | InterfaceRole.objects.filter(device_roles=device.role)
            self.fields["interface_role"].queryset = self.fields["interface_role"].queryset.distinct().order_by("name")


class InterfaceRoleAssignmentFilterSetForm(NetBoxModelFilterSetForm):
    """Filter form for the InterfaceRoleAssignment list view."""

    model = InterfaceRoleAssignment

    interface_id = DynamicModelMultipleChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_("Interface"),
    )
    interface_role_id = DynamicModelMultipleChoiceField(
        queryset=InterfaceRole.objects.all(),
        required=False,
        label=_("Interface Role"),
    )
    interface_role_group_id = DynamicModelMultipleChoiceField(
        queryset=RoleGroup.objects.all(),
        required=False,
        null_option="None",
        label=_("Role Group"),
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_("Device"),
    )
