"""
ProfileConfigTemplate forms for netbox interface profiles.
"""

from core.forms.mixins import SyncedDataMixin
from core.models import DataFile, DataSource
from dcim.models import DeviceType, Platform
from django import forms
from django.utils.translation import gettext_lazy as _
from extras.models import Tag
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm, NetBoxModelImportForm
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES
from utilities.forms.fields import (
    CSVModelChoiceField,
    CSVModelMultipleChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from ..models import InterfaceRole, ProfileConfigTemplate
from ..widgets import ProfileNameWidget


class ProfileConfigTemplateForm(SyncedDataMixin, NetBoxModelForm):
    """Create / Edit form for ProfileConfigTemplate."""

    interface_role = DynamicModelChoiceField(
        queryset=InterfaceRole.objects.all(),
        label=_("Interface Role"),
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
    device_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label=_("Device Tags"),
        help_text=_("If specified, the template only applies to devices with all of these tags."),
    )
    interface_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label=_("Interface Tags"),
        help_text=_("If specified, the template only applies to interfaces with all of these tags."),
    )
    template_code = forms.CharField(
        label=_("Template Code"),
        required=False,
        help_text=_("Jinja2 template code used to render the interface configuration."),
        widget=forms.Textarea(attrs={"class": "font-monospace", "rows": 12}),
    )

    name = forms.CharField(
        label=_("Name"),
        help_text=_(
            "Unique name for this profile config template. Use the Generate button to derive it from the scope fields."
        ),
        widget=ProfileNameWidget(),
    )

    fieldsets = (
        FieldSet(
            "interface_role", "platform", "device_type", "device_tags", "interface_tags", "weight", name=_("Scope")
        ),
        FieldSet("name", "description", "tags", name=_("Profile Config Template")),
        FieldSet("template_code", name=_("Template")),
        FieldSet("data_source", "data_file", "auto_sync_enabled", name=_("Data Source")),
        FieldSet("environment_params", "debug", name=_("Rendering")),
    )

    class Meta:
        model = ProfileConfigTemplate
        fields = (
            "name",
            "description",
            "interface_role",
            "platform",
            "device_type",
            "device_tags",
            "interface_tags",
            "weight",
            "template_code",
            "data_source",
            "data_file",
            "auto_sync_enabled",
            "environment_params",
            "debug",
            "tags",
        )
        widgets = {
            "environment_params": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Template code is read-only when it is synchronized from a data file
        if self.instance.data_file:
            self.fields["template_code"].widget.attrs["readonly"] = True
            self.fields["template_code"].help_text = _(
                "Template content is populated from the remote source selected below."
            )

    def clean(self):
        super().clean()

        if not self.cleaned_data.get("template_code") and not self.cleaned_data.get("data_file"):
            raise forms.ValidationError(_("Must specify either local content or a data file"))

        return self.cleaned_data


class ProfileConfigTemplateImportForm(NetBoxModelImportForm):
    """CSV import form for ProfileConfigTemplate."""

    interface_role = CSVModelChoiceField(
        queryset=InterfaceRole.objects.all(),
        to_field_name="name",
        label=_("Interface Role"),
    )
    platform = CSVModelChoiceField(
        queryset=Platform.objects.all(),
        to_field_name="slug",
        label=_("Platform"),
    )
    device_type = CSVModelChoiceField(
        queryset=DeviceType.objects.all(),
        to_field_name="slug",
        required=False,
        label=_("Device Type"),
    )
    device_tags = CSVModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        to_field_name="slug",
        required=False,
        label=_("Device Tags"),
    )
    interface_tags = CSVModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        to_field_name="slug",
        required=False,
        label=_("Interface Tags"),
    )
    data_source = CSVModelChoiceField(
        queryset=DataSource.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Data Source"),
    )
    data_file = CSVModelChoiceField(
        queryset=DataFile.objects.all(),
        to_field_name="path",
        required=False,
        label=_("Data File"),
    )

    class Meta:
        model = ProfileConfigTemplate
        fields = (
            "name",
            "description",
            "interface_role",
            "platform",
            "device_type",
            "device_tags",
            "interface_tags",
            "weight",
            "template_code",
            "data_source",
            "data_file",
            "auto_sync_enabled",
            "environment_params",
            "debug",
            "tags",
        )

    def clean_data_source(self):
        # Paths are unique only within a source, and Meta.fields cleans data_source before data_file
        data_source = self.cleaned_data.get("data_source")
        if data_source:
            self.fields["data_file"].queryset = self.fields["data_file"].queryset.filter(source=data_source)

        return data_source

    def clean(self):
        super().clean()

        if not self.data.get("template_code") and not self.data.get("data_file"):
            raise forms.ValidationError(_("Must specify either local content or a data file"))

        return self.cleaned_data


class ProfileConfigTemplateBulkEditForm(NetBoxModelBulkEditForm):
    """Bulk edit form for ProfileConfigTemplate."""

    model = ProfileConfigTemplate

    pk = forms.ModelMultipleChoiceField(
        queryset=ProfileConfigTemplate.objects.all(),
        widget=forms.MultipleHiddenInput(),
    )
    interface_role = DynamicModelChoiceField(
        queryset=InterfaceRole.objects.all(),
        required=False,
        label=_("Interface Role"),
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
    weight = forms.IntegerField(min_value=0, required=False, label=_("Weight"))
    description = forms.CharField(max_length=200, required=False)
    auto_sync_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Auto Sync Enabled"),
    )
    debug = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Debug"),
    )

    fieldsets = (
        FieldSet("interface_role", "platform", "device_type", "weight", name=_("Scope")),
        FieldSet("description", "auto_sync_enabled", "debug", name=_("Profile Config Template")),
    )
    nullable_fields = ("device_type", "description")


class ProfileConfigTemplateFilterSetForm(NetBoxModelFilterSetForm):
    """Filter form for the ProfileConfigTemplate list view."""

    model = ProfileConfigTemplate

    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet(
            "interface_role_id",
            "platform_id",
            "device_type_id",
            "device_tag_id",
            "interface_tag_id",
            name=_("Scope"),
        ),
        FieldSet("data_source_id", "data_file_id", "auto_sync_enabled", name=_("Data")),
    )

    tag = TagFilterField(model)
    interface_role_id = DynamicModelMultipleChoiceField(
        queryset=InterfaceRole.objects.all(),
        required=False,
        label=_("Interface Role"),
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
    device_tag_id = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label=_("Device Tags"),
    )
    interface_tag_id = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label=_("Interface Tags"),
    )
    data_source_id = DynamicModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        label=_("Data Source"),
    )
    data_file_id = DynamicModelMultipleChoiceField(
        queryset=DataFile.objects.all(),
        required=False,
        label=_("Data File"),
        query_params={"source_id": "$data_source_id"},
    )
    auto_sync_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Auto Sync Enabled"),
    )
