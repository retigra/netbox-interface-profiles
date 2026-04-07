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
from utilities.forms.fields import DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet

from ..models import InterfaceProfile


class InterfaceProfileForm(NetBoxModelForm):
    """Create / Edit form for InterfaceProfile."""

    device_roles = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_("Device Roles"),
        help_text=_(
            "If specified, this profile is only available for assignment to interfaces on devices with these roles. If empty, profile is available for all devices."
        ),
    )

    fieldsets = (
        FieldSet("name", "description", "tags", name=_("Interface Profile")),
        FieldSet("device_roles", name=_("Scope")),
    )

    class Meta:
        model = InterfaceProfile
        fields = ("name", "description", "device_roles", "tags")


class InterfaceProfileImportForm(NetBoxModelImportForm):
    """CSV import form for InterfaceProfile."""

    class Meta:
        model = InterfaceProfile
        fields = ("name", "description", "device_roles")


class InterfaceProfileBulkEditForm(NetBoxModelBulkEditForm):
    """Bulk edit form for InterfaceProfile."""

    model = InterfaceProfile

    pk = forms.ModelMultipleChoiceField(
        queryset=InterfaceProfile.objects.all(),
        widget=forms.MultipleHiddenInput(),
    )
    description = forms.CharField(max_length=200, required=False)
    device_roles = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_("Device Roles"),
    )

    class Meta:
        nullable_fields = ("description",)


class InterfaceProfileFilterSetForm(NetBoxModelFilterSetForm):
    """Filter form for the InterfaceProfile list view."""

    model = InterfaceProfile
    name = forms.CharField(required=False)
    description = forms.CharField(required=False)
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
        help_text=_("Compute and log diffs without committing interface changes to the database."),
    )
