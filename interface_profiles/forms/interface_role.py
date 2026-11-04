"""
InterfaceRole forms for interface profiles.
"""

from dcim.models import DeviceRole
from django import forms
from django.utils.translation.trans_null import _
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from utilities.forms.fields import CSVModelChoiceField, DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet

from ..models import InterfaceRole, RoleGroup


class InterfaceRoleForm(NetBoxModelForm):
    """Create / Edit form for InterfaceRole."""

    group = DynamicModelChoiceField(
        queryset=RoleGroup.objects.all(),
        required=False,
        label=_("Group"),
        help_text=_("Assignment permissions can be constrained on the role group."),
    )
    device_roles = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_("Device Roles"),
        help_text=_(
            "If specified, this role is only available for assignment to interfaces on devices with these device roles. If empty, role is available for all devices."
        ),
    )

    fieldsets = (
        FieldSet("name", "group", "description", "tags", name=_("Interface Role")),
        FieldSet("device_roles", name=_("Scope")),
    )

    class Meta:
        model = InterfaceRole
        fields = ("name", "group", "description", "device_roles", "tags")


class InterfaceRoleImportForm(NetBoxModelImportForm):
    """CSV import form for InterfaceRole."""

    group = CSVModelChoiceField(
        queryset=RoleGroup.objects.all(),
        required=False,
        to_field_name="name",
        label=_("Group"),
        help_text=_("Name of the role group"),
    )

    class Meta:
        model = InterfaceRole
        fields = ("name", "group", "description", "device_roles")


class InterfaceRoleBulkEditForm(NetBoxModelBulkEditForm):
    """Bulk edit form for InterfaceRole."""

    model = InterfaceRole

    pk = forms.ModelMultipleChoiceField(
        queryset=InterfaceRole.objects.all(),
        widget=forms.MultipleHiddenInput(),
    )
    group = DynamicModelChoiceField(
        queryset=RoleGroup.objects.all(),
        required=False,
        label=_("Group"),
    )
    description = forms.CharField(max_length=200, required=False)
    device_roles = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_("Device Roles"),
    )

    class Meta:
        nullable_fields = ("group", "description")


class InterfaceRoleFilterSetForm(NetBoxModelFilterSetForm):
    """Filter form for the InterfaceRole list view."""

    model = InterfaceRole
    name = forms.CharField(required=False)
    description = forms.CharField(required=False)
    group_id = DynamicModelMultipleChoiceField(
        queryset=RoleGroup.objects.all(),
        required=False,
        null_option="None",
        label=_("Group"),
    )
    device_roles = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_("Device Roles"),
    )


class InterfaceRoleSyncForm(forms.Form):
    """Form for triggering role-wide interface synchronization."""

    dry_run = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Dry run"),
        help_text=_("Only show the changes that would be made, without saving them. They can be applied afterwards."),
    )
