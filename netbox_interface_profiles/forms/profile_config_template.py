"""
ProfileConfigTemplate forms for netbox interface profiles.
"""

from dcim.models import DeviceType, Platform
from django import forms
from django.utils.translation import gettext_lazy as _
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm, NetBoxModelImportForm
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet

from ..models import InterfaceProfile, ProfileConfigTemplate


class ProfileConfigTemplateForm(NetBoxModelForm):
    """Create / Edit form for ProfileConfigTemplate."""

    interface_profile = DynamicModelChoiceField(
        queryset=InterfaceProfile.objects.all(),
        label=_("Interface Profile"),
    )
    platform = DynamicModelChoiceField(
        queryset=Platform.objects.all(),
        label=_("Platform"),
    )
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        label=_("Device Type"),
    )
    template_code = forms.CharField(
        label=_("Template Code"),
        help_text=_("Jinja2 template code used to render the interface configuration."),
        widget=forms.Textarea(attrs={"class": "font-monospace", "rows": 12}),
    )

    name = forms.CharField(
        label=_("Name"),
        help_text=_("Unique name for this profile config template."),
    )

    fieldsets = (
        FieldSet("interface_profile", "platform", "device_type", name=_("Scope")),
        FieldSet("name", "description", "tags", name=_("Profile Config Template")),
        FieldSet("template_code", name=_("Template")),
    )

    class Meta:
        model = ProfileConfigTemplate
        fields = (
            "name",
            "description",
            "interface_profile",
            "platform",
            "device_type",
            "template_code",
            "tags",
        )


class ProfileConfigTemplateImportForm(NetBoxModelImportForm):
    """CSV import form for ProfileConfigTemplate."""

    class Meta:
        model = ProfileConfigTemplate
        fields = (
            "name",
            "description",
            "interface_profile",
            "platform",
            "device_type",
            "template_code",
        )


class ProfileConfigTemplateBulkEditForm(NetBoxModelBulkEditForm):
    """Bulk edit form for ProfileConfigTemplate."""

    model = ProfileConfigTemplate

    pk = forms.ModelMultipleChoiceField(
        queryset=ProfileConfigTemplate.objects.all(),
        widget=forms.MultipleHiddenInput(),
    )
    interface_profile = DynamicModelChoiceField(
        queryset=InterfaceProfile.objects.all(),
        required=False,
        label=_("Interface Profile"),
    )
    platform = DynamicModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        label=_("Platform"),
    )
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        label=_("Device Type"),
    )
    description = forms.CharField(max_length=200, required=False)

    class Meta:
        nullable_fields = ("device_type", "description")


class ProfileConfigTemplateFilterSetForm(NetBoxModelFilterSetForm):
    """Filter form for the ProfileConfigTemplate list view."""

    model = ProfileConfigTemplate

    name = forms.CharField(required=False)
    interface_profile_id = DynamicModelMultipleChoiceField(
        queryset=InterfaceProfile.objects.all(),
        required=False,
        label=_("Interface Profile"),
    )
    platform_id = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        label=_("Platform"),
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        label=_("Device Type"),
    )
