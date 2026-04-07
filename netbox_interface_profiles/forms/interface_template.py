"""
InterfaceTemplate forms for netbox interface profiles.
"""

from dcim.models import SiteGroup
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

from ..models import InterfaceProfile, InterfaceTemplate


class InterfaceTemplateForm(NetBoxModelForm):
    """Create / Edit form for InterfaceTemplate."""

    interface_profile = DynamicModelChoiceField(
        queryset=InterfaceProfile.objects.all(),
        label=_("Interface Profile"),
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_("Site Group"),
        help_text=_("Optional scope. If null, template is globally reusable."),
    )

    # Speed, duplex, MTU
    speed = forms.IntegerField(
        required=False,
        min_value=0,
        label=_("Speed (Mbps)"),
        help_text=_("Interface speed in megabits per second (e.g., 1000, 10000)"),
    )
    duplex = forms.ChoiceField(
        choices=[("", "———"), ("auto", "Auto"), ("half", "Half"), ("full", "Full")],
        required=False,
        label=_("Duplex"),
    )
    mtu = forms.IntegerField(
        required=False,
        min_value=0,
        label=_("MTU"),
        help_text=_("Maximum transmission unit in bytes"),
    )

    # Mode
    mode = forms.ChoiceField(
        choices=[
            ("", "———"),
            ("access", "Access"),
            ("tagged", "Tagged"),
            ("tagged-all", "Tagged All"),
        ],
        required=False,
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
        FieldSet("interface_profile", "site_group", name=_("Scope")),
        FieldSet("name", "description", "tags", name=_("Basic Information")),
        FieldSet("speed", "duplex", "mtu", "enabled", name=_("Physical Configuration")),
        FieldSet("mode", name=_("Layer 2 Configuration")),
        FieldSet("untagged_vlan_vid", "tagged_vlans_vids", name=_("VLAN Configuration")),
        FieldSet("poe_mode", name=_("POE Configuration")),
    )

    class Meta:
        model = InterfaceTemplate
        fields = (
            "name",
            "description",
            "interface_profile",
            "site_group",
            "speed",
            "duplex",
            "mtu",
            "mode",
            "enabled",
            "poe_mode",
            "untagged_vlan_vid",
            "tagged_vlans_vids",
            "tags",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tagged_vlans = self.initial.get("tagged_vlans_vids")
        if isinstance(tagged_vlans, list):
            self.initial["tagged_vlans_vids"] = ",".join(str(vid) for vid in tagged_vlans)

    def clean_tagged_vlans_vids(self):
        """Convert comma-separated VIDs string to JSON list."""
        data = self.cleaned_data.get("tagged_vlans_vids", "").strip()
        if not data:
            return []
        try:
            vids = [int(vid.strip()) for vid in data.split(",") if vid.strip()]
            # Validate VLAN VID range
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
            "interface_profile",
            "site_group",
            "speed",
            "duplex",
            "mtu",
            "mode",
            "enabled",
            "poe_mode",
            "untagged_vlan_vid",
            "tagged_vlans_vids",
        )


class InterfaceTemplateBulkEditForm(NetBoxModelBulkEditForm):
    """Bulk edit form for InterfaceTemplate."""

    model = InterfaceTemplate

    pk = forms.ModelMultipleChoiceField(
        queryset=InterfaceTemplate.objects.all(),
        widget=forms.MultipleHiddenInput(),
    )
    interface_profile = DynamicModelChoiceField(
        queryset=InterfaceProfile.objects.all(),
        required=False,
        label=_("Interface Profile"),
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_("Site Group"),
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

    class Meta:
        nullable_fields = ("description", "site_group", "speed", "duplex", "mtu", "mode", "poe_mode")


class InterfaceTemplateFilterSetForm(NetBoxModelFilterSetForm):
    """Filter form for the InterfaceTemplate list view."""

    model = InterfaceTemplate

    name = forms.CharField(required=False, label=_("Name"))
    description = forms.CharField(required=False, label=_("Description"))
    interface_profile_id = DynamicModelMultipleChoiceField(
        queryset=InterfaceProfile.objects.all(),
        required=False,
        label=_("Interface Profile"),
    )
    site_group_id = DynamicModelMultipleChoiceField(
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
