"""
InterfaceProfile forms for netbox interface profiles.
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

from ..models import InterfaceProfile, ProfileGroup


class InterfaceProfileForm(NetBoxModelForm):
    """Create / Edit form for InterfaceProfile."""

    group = DynamicModelChoiceField(
        queryset=ProfileGroup.objects.all(),
        required=False,
        label=_("Group"),
        help_text=_("Assignment permissions can be constrained on the profile group."),
    )
    device_roles = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_("Device Roles"),
        help_text=_(
            "If specified, this profile is only available for assignment to interfaces on devices with these roles. If empty, profile is available for all devices."
        ),
    )

    fieldsets = (
        FieldSet("name", "group", "description", "tags", name=_("Interface Profile")),
        FieldSet("device_roles", name=_("Scope")),
    )

    class Meta:
        model = InterfaceProfile
        fields = ("name", "group", "description", "device_roles", "tags")


class InterfaceProfileImportForm(NetBoxModelImportForm):
    """CSV import form for InterfaceProfile."""

    group = CSVModelChoiceField(
        queryset=ProfileGroup.objects.all(),
        required=False,
        to_field_name="name",
        label=_("Group"),
        help_text=_("Name of the profile group"),
    )

    class Meta:
        model = InterfaceProfile
        fields = ("name", "group", "description", "device_roles")


class InterfaceProfileBulkEditForm(NetBoxModelBulkEditForm):
    """Bulk edit form for InterfaceProfile."""

    model = InterfaceProfile

    pk = forms.ModelMultipleChoiceField(
        queryset=InterfaceProfile.objects.all(),
        widget=forms.MultipleHiddenInput(),
    )
    group = DynamicModelChoiceField(
        queryset=ProfileGroup.objects.all(),
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


class InterfaceProfileFilterSetForm(NetBoxModelFilterSetForm):
    """Filter form for the InterfaceProfile list view."""

    model = InterfaceProfile
    name = forms.CharField(required=False)
    description = forms.CharField(required=False)
    group_id = DynamicModelMultipleChoiceField(
        queryset=ProfileGroup.objects.all(),
        required=False,
        null_option="None",
        label=_("Group"),
    )
    device_roles = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_("Device Roles"),
    )


class InterfaceProfileSyncForm(forms.Form):
    """Form for triggering profile-wide interface synchronization."""

    dry_run = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Dry run"),
        help_text=_("Only show the changes that would be made, without saving them. They can be applied afterwards."),
    )
