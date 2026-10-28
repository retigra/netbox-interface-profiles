"""
InterfaceTemplate forms for netbox interface profiles.
"""

from dcim.models import Site, SiteGroup
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from utilities.forms import get_field_value
from utilities.forms.fields import ContentTypeChoiceField, DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import BulkEditNullBooleanSelect, HTMXSelect
from utilities.templatetags.builtins.filters import bettertitle

from ..models import InterfaceRole, InterfaceTemplate

INTERFACE_TEMPLATE_SCOPE_TYPES = ("site", "sitegroup")


class InterfaceTemplateForm(NetBoxModelForm):
    """Create / Edit form for InterfaceTemplate."""

    interface_role = DynamicModelChoiceField(
        queryset=InterfaceRole.objects.all(),
        label=_("Interface Role"),
    )
    scope_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(app_label="dcim", model__in=INTERFACE_TEMPLATE_SCOPE_TYPES),
        widget=HTMXSelect(),
        required=False,
        label=_("Scope type"),
    )
    scope = DynamicModelChoiceField(
        label=_("Scope"),
        queryset=Site.objects.none(),
        required=False,
        disabled=True,
        selector=True,
    )

    # Speed, duplex, MTU
    speed = forms.IntegerField(
        required=False,
        min_value=0,
        label=_("Speed (Mbps)"),
        help_text=_("Interface speed in megabits per second (e.g., 1000, 10000)"),
    )
    duplex = forms.TypedChoiceField(
        choices=[("", "———"), ("auto", "Auto"), ("half", "Half"), ("full", "Full")],
        required=False,
        empty_value=None,
        label=_("Duplex"),
    )
    mtu = forms.IntegerField(
        required=False,
        min_value=0,
        label=_("MTU"),
        help_text=_("Maximum transmission unit in bytes"),
    )

    # Mode
    mode = forms.TypedChoiceField(
        choices=[
            ("", "———"),
            ("access", "Access"),
            ("tagged", "Tagged"),
            ("tagged-all", "Tagged All"),
        ],
        required=False,
        empty_value=None,
        label=_("Mode"),
        help_text=_("Interface mode (access/tagged/tagged-all)"),
    )

    # Enabled & POE
    enabled = forms.BooleanField(
        required=False,
        label=_("Enabled"),
        help_text=_("Whether the interface is enabled by default"),
    )
    poe_mode = forms.CharField(
        max_length=50,
        required=False,
        empty_value=None,
        label=_("POE Mode"),
        help_text=_("POE mode (power-supply, power-device, etc.)"),
    )

    # VLAN references
    untagged_vlan_vid = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=4094,
        label=_("Untagged VLAN VID"),
        help_text=_("Untagged VLAN ID. Will be resolved to actual VLAN in target site."),
    )
    tagged_vlans_vids = forms.CharField(
        required=False,
        label=_("Tagged VLAN VIDs"),
        help_text=_("Comma-separated list of tagged VLAN IDs (e.g., 100,200,300)"),
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    fieldsets = (
        FieldSet("interface_role", "scope_type", "scope", name=_("Scope")),
        FieldSet("name", "description", "tags", name=_("Basic Information")),
        FieldSet(
            "speed",
            "set_null_speed",
            "duplex",
            "set_null_duplex",
            "mtu",
            "set_null_mtu",
            "enabled",
            name=_("Physical Configuration"),
        ),
        FieldSet("mode", "set_null_mode", name=_("Layer 2 Configuration")),
        FieldSet(
            "untagged_vlan_vid",
            "set_null_untagged_vlan_vid",
            "tagged_vlans_vids",
            name=_("VLAN Configuration"),
        ),
        FieldSet("poe_mode", "set_null_poe_mode", name=_("POE Configuration")),
    )

    class Meta:
        model = InterfaceTemplate
        fields = (
            "name",
            "description",
            "interface_role",
            "scope_type",
            "speed",
            "duplex",
            "mtu",
            "mode",
            "enabled",
            "poe_mode",
            "untagged_vlan_vid",
            "tagged_vlans_vids",
            "set_null_speed",
            "set_null_duplex",
            "set_null_mtu",
            "set_null_mode",
            "set_null_poe_mode",
            "set_null_untagged_vlan_vid",
            "tags",
        )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {})

        if instance is not None and instance.scope:
            initial["scope"] = instance.scope
            kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        tagged_vlans = self.initial.get("tagged_vlans_vids")
        if isinstance(tagged_vlans, list):
            self.initial["tagged_vlans_vids"] = ",".join(str(vid) for vid in tagged_vlans)

        if scope_type_id := get_field_value(self, "scope_type"):
            try:
                scope_type = ContentType.objects.get(pk=scope_type_id)
                model = scope_type.model_class()
                self.fields["scope"].queryset = model.objects.all()
                self.fields["scope"].widget.attrs["selector"] = model._meta.label_lower
                self.fields["scope"].disabled = False
                self.fields["scope"].label = _(bettertitle(model._meta.verbose_name))
            except ObjectDoesNotExist:
                pass

            if self.instance and scope_type_id != self.instance.scope_type_id:
                self.initial["scope"] = None

    def clean(self):
        super().clean()
        self.instance.scope = self.cleaned_data.get("scope")

    def clean_tagged_vlans_vids(self):
        """Convert comma-separated VIDs string to JSON list."""
        data = self.cleaned_data.get("tagged_vlans_vids", "").strip()
        if not data:
            return []
        try:
            vids = [int(vid.strip()) for vid in data.split(",") if vid.strip()]
            for vid in vids:
                if not (0 <= vid <= 4094):
                    raise forms.ValidationError(
                        _("VLAN VID must be between 0 and 4094. Got: %(value)s"),
                        code="invalid_vlan_vid",
                        params={"value": vid},
                    )
            return vids
        except ValueError as exc:
            raise forms.ValidationError(
                _("Tagged VLAN VIDs must be comma-separated integers."),
                code="invalid_format",
            ) from exc

    def clean_enabled(self):
        """Ensure enabled is always a boolean."""
        return self.cleaned_data.get("enabled", True)


class InterfaceTemplateImportForm(NetBoxModelImportForm):
    """CSV import form for InterfaceTemplate."""

    class Meta:
        model = InterfaceTemplate
        fields = (
            "name",
            "description",
            "interface_role",
            "speed",
            "duplex",
            "mtu",
            "mode",
            "enabled",
            "poe_mode",
            "untagged_vlan_vid",
            "tagged_vlans_vids",
            "set_null_speed",
            "set_null_duplex",
            "set_null_mtu",
            "set_null_mode",
            "set_null_poe_mode",
            "set_null_untagged_vlan_vid",
        )


class InterfaceTemplateBulkEditForm(NetBoxModelBulkEditForm):
    """Bulk edit form for InterfaceTemplate."""

    model = InterfaceTemplate

    pk = forms.ModelMultipleChoiceField(
        queryset=InterfaceTemplate.objects.all(),
        widget=forms.MultipleHiddenInput(),
    )
    interface_role = DynamicModelChoiceField(
        queryset=InterfaceRole.objects.all(),
        required=False,
        label=_("Interface Role"),
    )
    scope_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(app_label="dcim", model__in=INTERFACE_TEMPLATE_SCOPE_TYPES),
        widget=HTMXSelect(method="post", attrs={"hx-select": "#form_fields"}),
        required=False,
        label=_("Scope type"),
    )
    scope = DynamicModelChoiceField(
        label=_("Scope"),
        queryset=Site.objects.none(),
        required=False,
        disabled=True,
        selector=True,
    )
    speed = forms.IntegerField(required=False, min_value=0, label=_("Speed (Mbps)"))
    duplex = forms.ChoiceField(
        choices=[("", "———"), ("auto", "Auto"), ("half", "Half"), ("full", "Full")],
        required=False,
        label=_("Duplex"),
    )
    mtu = forms.IntegerField(required=False, min_value=0, label=_("MTU"))
    mode = forms.ChoiceField(
        choices=[
            ("", "———"),
            ("access", "Access"),
            ("tagged", "Tagged"),
            ("tagged-all", "Tagged All"),
        ],
        required=False,
        label=_("Mode"),
    )
    enabled = forms.NullBooleanField(
        required=False,
        label=_("Enabled"),
        widget=forms.Select(choices=[("", "———"), (True, "Yes"), (False, "No")]),
    )
    poe_mode = forms.CharField(max_length=50, required=False, label=_("POE Mode"))
    description = forms.CharField(max_length=200, required=False)
    set_null_speed = forms.NullBooleanField(required=False, label=_("Clear speed"), widget=BulkEditNullBooleanSelect())
    set_null_duplex = forms.NullBooleanField(
        required=False, label=_("Clear duplex"), widget=BulkEditNullBooleanSelect()
    )
    set_null_mtu = forms.NullBooleanField(required=False, label=_("Clear MTU"), widget=BulkEditNullBooleanSelect())
    set_null_mode = forms.NullBooleanField(required=False, label=_("Clear mode"), widget=BulkEditNullBooleanSelect())
    set_null_poe_mode = forms.NullBooleanField(
        required=False, label=_("Clear POE mode"), widget=BulkEditNullBooleanSelect()
    )
    set_null_untagged_vlan_vid = forms.NullBooleanField(
        required=False, label=_("Clear untagged VLAN"), widget=BulkEditNullBooleanSelect()
    )

    class Meta:
        nullable_fields = ("description", "scope", "speed", "duplex", "mtu", "mode", "poe_mode")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if scope_type_id := get_field_value(self, "scope_type"):
            try:
                scope_type = ContentType.objects.get(pk=scope_type_id)
                model = scope_type.model_class()
                self.fields["scope"].queryset = model.objects.all()
                self.fields["scope"].widget.attrs["selector"] = model._meta.label_lower
                self.fields["scope"].disabled = False
                self.fields["scope"].label = _(bettertitle(model._meta.verbose_name))
            except ObjectDoesNotExist:
                pass


class InterfaceTemplateFilterSetForm(NetBoxModelFilterSetForm):
    """Filter form for the InterfaceTemplate list view."""

    model = InterfaceTemplate

    name = forms.CharField(required=False, label=_("Name"))
    description = forms.CharField(required=False, label=_("Description"))
    interface_role_id = DynamicModelMultipleChoiceField(
        queryset=InterfaceRole.objects.all(),
        required=False,
        label=_("Interface Role"),
    )
    scope_site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_("Site"),
    )
    scope_site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_("Site Group"),
    )
    speed = forms.IntegerField(required=False, label=_("Speed (Mbps)"))
    duplex = forms.ChoiceField(
        choices=[("", "———"), ("auto", "Auto"), ("half", "Half"), ("full", "Full")],
        required=False,
        label=_("Duplex"),
    )
    mtu = forms.IntegerField(required=False, label=_("MTU"))
    mode = forms.ChoiceField(
        choices=[
            ("", "———"),
            ("access", "Access"),
            ("tagged", "Tagged"),
            ("tagged-all", "Tagged All"),
        ],
        required=False,
        label=_("Mode"),
    )
    enabled = forms.NullBooleanField(
        required=False,
        label=_("Enabled"),
        widget=forms.Select(choices=[("", "———"), (True, "Yes"), (False, "No")]),
    )
    poe_mode = forms.CharField(required=False, label=_("POE Mode"))
