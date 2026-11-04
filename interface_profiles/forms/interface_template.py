"""
InterfaceTemplate forms for interface profiles.
"""

from dcim.choices import (
    InterfaceDuplexChoices,
    InterfaceModeChoices,
    InterfacePoEModeChoices,
    InterfacePoETypeChoices,
    InterfaceSpeedChoices,
)
from dcim.constants import INTERFACE_MTU_MAX, INTERFACE_MTU_MIN
from dcim.models import Site, SiteGroup
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from ipam.constants import VLAN_VID_MAX, VLAN_VID_MIN
from ipam.models import VRF, VLANTranslationPolicy
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from utilities.forms import add_blank_choice, get_field_value
from utilities.forms.fields import (
    ContentTypeChoiceField,
    CSVChoiceField,
    CSVContentTypeField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    PositiveBigIntegerField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.utils import parse_numeric_range
from utilities.forms.widgets import BulkEditNullBooleanSelect, HTMXSelect, NumberWithOptions
from utilities.templatetags.builtins.filters import bettertitle

from ..models import InterfaceRole, InterfaceTemplate

INTERFACE_TEMPLATE_SCOPE_TYPES = ("site", "sitegroup")

# Interface attribute fields shared by the edit and import forms, in display order
ATTRIBUTE_FIELDS = (
    "enabled",
    "mgmt_only",
    "interface_description",
    "set_null_interface_description",
    "speed",
    "set_null_speed",
    "duplex",
    "set_null_duplex",
    "mtu",
    "set_null_mtu",
    "vrf",
    "set_null_vrf",
    "mode",
    "set_null_mode",
    "untagged_vlan_vid",
    "set_null_untagged_vlan_vid",
    "tagged_vlans_vids",
    "qinq_svlan_vid",
    "set_null_qinq_svlan_vid",
    "vlan_translation_policy",
    "set_null_vlan_translation_policy",
    "poe_mode",
    "set_null_poe_mode",
    "poe_type",
    "set_null_poe_type",
)


def _scope_type_queryset():
    return ContentType.objects.filter(app_label="dcim", model__in=INTERFACE_TEMPLATE_SCOPE_TYPES)


def _enable_scope_field(form: forms.Form) -> None:
    """Limit the scope field to objects of the selected scope type."""
    if scope_type_id := get_field_value(form, "scope_type"):
        try:
            scope_type = ContentType.objects.get(pk=scope_type_id)
        except (ObjectDoesNotExist, ValueError):
            return
        model = scope_type.model_class()
        field = form.fields["scope"]
        field.queryset = model.objects.all()
        field.widget.attrs["selector"] = model._meta.label_lower
        field.disabled = False
        field.label = _(bettertitle(model._meta.verbose_name))


class UnchangedNullBooleanSelect(forms.NullBooleanSelect):
    """A yes/no select whose empty option leaves the interface attribute unchanged."""

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.choices = (("unknown", "———"), ("true", _("Yes")), ("false", _("No")))


class TaggedVLANVIDsField(forms.CharField):
    """A list of VIDs entered as comma-separated numbers and ranges, e.g. `100,200-205`."""

    def __init__(self, **kwargs):
        kwargs.setdefault("help_text", _("Comma-separated VIDs and ranges, e.g. 100,200-205"))
        super().__init__(**kwargs)

    def prepare_value(self, value):
        if isinstance(value, list):
            return ",".join(str(vid) for vid in value)
        return value

    def to_python(self, value):
        value = super().to_python(value).strip()
        if not value:
            return []
        return parse_numeric_range(value, min_value=VLAN_VID_MIN, max_value=VLAN_VID_MAX)


class InterfaceTemplateForm(NetBoxModelForm):
    """Create / Edit form for InterfaceTemplate."""

    interface_role = DynamicModelChoiceField(
        queryset=InterfaceRole.objects.all(),
        label=_("Interface Role"),
    )
    scope_type = ContentTypeChoiceField(
        queryset=_scope_type_queryset(),
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
    mgmt_only = forms.NullBooleanField(
        required=False,
        widget=UnchangedNullBooleanSelect(),
        label=_("Management only"),
        help_text=_("Empty leaves the interface unchanged"),
    )
    speed = PositiveBigIntegerField(
        required=False,
        widget=NumberWithOptions(options=InterfaceSpeedChoices),
        label=_("Speed (Kbps)"),
    )
    duplex = forms.TypedChoiceField(
        choices=add_blank_choice(InterfaceDuplexChoices),
        required=False,
        empty_value=None,
        label=_("Duplex"),
    )
    mode = forms.TypedChoiceField(
        choices=add_blank_choice(InterfaceModeChoices),
        required=False,
        empty_value=None,
        label=_("802.1Q mode"),
    )
    poe_mode = forms.TypedChoiceField(
        choices=add_blank_choice(InterfacePoEModeChoices),
        required=False,
        empty_value=None,
        label=_("PoE mode"),
    )
    poe_type = forms.TypedChoiceField(
        choices=add_blank_choice(InterfacePoETypeChoices),
        required=False,
        empty_value=None,
        label=_("PoE type"),
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_("VRF"),
    )
    vlan_translation_policy = DynamicModelChoiceField(
        queryset=VLANTranslationPolicy.objects.all(),
        required=False,
        label=_("VLAN translation policy"),
    )
    tagged_vlans_vids = TaggedVLANVIDsField(required=False, label=_("Tagged VLAN VIDs"))

    fieldsets = (
        FieldSet("interface_role", "scope_type", "scope", name=_("Scope")),
        FieldSet("name", "description", "tags", name=_("Interface Template")),
        FieldSet(
            "enabled",
            "mgmt_only",
            "interface_description",
            "set_null_interface_description",
            name=_("General"),
        ),
        FieldSet(
            "speed",
            "set_null_speed",
            "duplex",
            "set_null_duplex",
            "mtu",
            "set_null_mtu",
            name=_("Physical"),
        ),
        FieldSet("vrf", "set_null_vrf", name=_("Addressing")),
        FieldSet(
            "mode",
            "set_null_mode",
            "untagged_vlan_vid",
            "set_null_untagged_vlan_vid",
            "tagged_vlans_vids",
            "qinq_svlan_vid",
            "set_null_qinq_svlan_vid",
            "vlan_translation_policy",
            "set_null_vlan_translation_policy",
            name=_("802.1Q Switching"),
        ),
        FieldSet("poe_mode", "set_null_poe_mode", "poe_type", "set_null_poe_type", name=_("Power over Ethernet")),
    )

    class Meta:
        model = InterfaceTemplate
        fields = ("interface_role", "scope_type", "name", "description", *ATTRIBUTE_FIELDS, "tags")

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {})

        if instance is not None and instance.scope:
            initial["scope"] = instance.scope
            kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        _enable_scope_field(self)
        if self.instance and get_field_value(self, "scope_type") != self.instance.scope_type_id:
            self.initial["scope"] = None

    def clean(self):
        super().clean()
        self.instance.scope = self.cleaned_data.get("scope")


class InterfaceTemplateImportForm(NetBoxModelImportForm):
    """CSV/YAML/JSON import form for InterfaceTemplate."""

    interface_role = CSVModelChoiceField(
        queryset=InterfaceRole.objects.all(),
        to_field_name="name",
        label=_("Interface role"),
        help_text=_("Name of the interface role"),
    )
    scope_type = CSVContentTypeField(
        queryset=_scope_type_queryset(),
        required=False,
        label=_("Scope type"),
        help_text=_("dcim.site or dcim.sitegroup. Leave empty for a global template."),
    )
    duplex = CSVChoiceField(choices=InterfaceDuplexChoices, required=False, label=_("Duplex"))
    mode = CSVChoiceField(choices=InterfaceModeChoices, required=False, label=_("802.1Q mode"))
    poe_mode = CSVChoiceField(choices=InterfacePoEModeChoices, required=False, label=_("PoE mode"))
    poe_type = CSVChoiceField(choices=InterfacePoETypeChoices, required=False, label=_("PoE type"))
    vrf = CSVModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        to_field_name="rd",
        label=_("VRF"),
        help_text=_("Route distinguisher of the VRF"),
    )
    vlan_translation_policy = CSVModelChoiceField(
        queryset=VLANTranslationPolicy.objects.all(),
        required=False,
        to_field_name="name",
        label=_("VLAN translation policy"),
    )
    tagged_vlans_vids = TaggedVLANVIDsField(required=False, label=_("Tagged VLAN VIDs"))

    class Meta:
        model = InterfaceTemplate
        fields = ("interface_role", "scope_type", "scope_id", "name", "description", *ATTRIBUTE_FIELDS, "tags")

    def clean_duplex(self):
        return self.cleaned_data["duplex"] or None

    def clean_mode(self):
        return self.cleaned_data["mode"] or None

    def clean_poe_mode(self):
        return self.cleaned_data["poe_mode"] or None

    def clean_poe_type(self):
        return self.cleaned_data["poe_type"] or None


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
        queryset=_scope_type_queryset(),
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
    description = forms.CharField(required=False, label=_("Description"))
    enabled = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect(), label=_("Enabled"))
    mgmt_only = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect(), label=_("Management only"))
    interface_description = forms.CharField(max_length=200, required=False, label=_("Interface description"))
    speed = PositiveBigIntegerField(
        required=False,
        widget=NumberWithOptions(options=InterfaceSpeedChoices),
        label=_("Speed (Kbps)"),
    )
    duplex = forms.ChoiceField(choices=add_blank_choice(InterfaceDuplexChoices), required=False, label=_("Duplex"))
    mtu = forms.IntegerField(required=False, min_value=INTERFACE_MTU_MIN, max_value=INTERFACE_MTU_MAX, label=_("MTU"))
    vrf = DynamicModelChoiceField(queryset=VRF.objects.all(), required=False, label=_("VRF"))
    mode = forms.ChoiceField(choices=add_blank_choice(InterfaceModeChoices), required=False, label=_("802.1Q mode"))
    untagged_vlan_vid = forms.IntegerField(
        required=False, min_value=VLAN_VID_MIN, max_value=VLAN_VID_MAX, label=_("Untagged VLAN VID")
    )
    tagged_vlans_vids = TaggedVLANVIDsField(required=False, label=_("Tagged VLAN VIDs"))
    qinq_svlan_vid = forms.IntegerField(
        required=False, min_value=VLAN_VID_MIN, max_value=VLAN_VID_MAX, label=_("Q-in-Q SVLAN VID")
    )
    vlan_translation_policy = DynamicModelChoiceField(
        queryset=VLANTranslationPolicy.objects.all(), required=False, label=_("VLAN translation policy")
    )
    poe_mode = forms.ChoiceField(choices=add_blank_choice(InterfacePoEModeChoices), required=False, label=_("PoE mode"))
    poe_type = forms.ChoiceField(choices=add_blank_choice(InterfacePoETypeChoices), required=False, label=_("PoE type"))

    set_null_interface_description = forms.NullBooleanField(
        required=False, widget=BulkEditNullBooleanSelect(), label=_("Clear interface description")
    )
    set_null_speed = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect(), label=_("Clear speed"))
    set_null_duplex = forms.NullBooleanField(
        required=False, widget=BulkEditNullBooleanSelect(), label=_("Clear duplex")
    )
    set_null_mtu = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect(), label=_("Clear MTU"))
    set_null_vrf = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect(), label=_("Clear VRF"))
    set_null_mode = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect(), label=_("Clear mode"))
    set_null_untagged_vlan_vid = forms.NullBooleanField(
        required=False, widget=BulkEditNullBooleanSelect(), label=_("Clear untagged VLAN")
    )
    set_null_qinq_svlan_vid = forms.NullBooleanField(
        required=False, widget=BulkEditNullBooleanSelect(), label=_("Clear Q-in-Q SVLAN")
    )
    set_null_vlan_translation_policy = forms.NullBooleanField(
        required=False, widget=BulkEditNullBooleanSelect(), label=_("Clear VLAN translation policy")
    )
    set_null_poe_mode = forms.NullBooleanField(
        required=False, widget=BulkEditNullBooleanSelect(), label=_("Clear PoE mode")
    )
    set_null_poe_type = forms.NullBooleanField(
        required=False, widget=BulkEditNullBooleanSelect(), label=_("Clear PoE type")
    )

    fieldsets = (
        FieldSet("interface_role", "scope_type", "scope", name=_("Scope")),
        FieldSet("description", name=_("Interface Template")),
        FieldSet("enabled", "mgmt_only", "interface_description", "set_null_interface_description", name=_("General")),
        FieldSet("speed", "set_null_speed", "duplex", "set_null_duplex", "mtu", "set_null_mtu", name=_("Physical")),
        FieldSet("vrf", "set_null_vrf", name=_("Addressing")),
        FieldSet(
            "mode",
            "set_null_mode",
            "untagged_vlan_vid",
            "set_null_untagged_vlan_vid",
            "tagged_vlans_vids",
            "qinq_svlan_vid",
            "set_null_qinq_svlan_vid",
            "vlan_translation_policy",
            "set_null_vlan_translation_policy",
            name=_("802.1Q Switching"),
        ),
        FieldSet("poe_mode", "set_null_poe_mode", "poe_type", "set_null_poe_type", name=_("Power over Ethernet")),
    )
    nullable_fields = (
        "description",
        "scope",
        "mgmt_only",
        "interface_description",
        "speed",
        "duplex",
        "mtu",
        "vrf",
        "mode",
        "untagged_vlan_vid",
        "qinq_svlan_vid",
        "vlan_translation_policy",
        "poe_mode",
        "poe_type",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _enable_scope_field(self)


class InterfaceTemplateFilterSetForm(NetBoxModelFilterSetForm):
    """Filter form for the InterfaceTemplate list view."""

    model = InterfaceTemplate

    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("interface_role_id", "scope_site_id", "scope_site_group_id", name=_("Scope")),
        FieldSet("enabled", "mgmt_only", "speed", "duplex", "mtu", "vrf_id", name=_("Attributes")),
        FieldSet(
            "mode",
            "untagged_vlan_vid",
            "tagged_vlan_vid",
            "qinq_svlan_vid",
            "vlan_translation_policy_id",
            name=_("802.1Q Switching"),
        ),
        FieldSet("poe_mode", "poe_type", name=_("Power over Ethernet")),
    )

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
    enabled = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect(), label=_("Enabled"))
    mgmt_only = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect(), label=_("Management only"))
    speed = PositiveBigIntegerField(
        required=False,
        widget=NumberWithOptions(options=InterfaceSpeedChoices),
        label=_("Speed (Kbps)"),
    )
    duplex = forms.MultipleChoiceField(choices=InterfaceDuplexChoices, required=False, label=_("Duplex"))
    mtu = forms.IntegerField(required=False, label=_("MTU"))
    vrf_id = DynamicModelMultipleChoiceField(queryset=VRF.objects.all(), required=False, label=_("VRF"))
    mode = forms.MultipleChoiceField(choices=InterfaceModeChoices, required=False, label=_("802.1Q mode"))
    untagged_vlan_vid = forms.IntegerField(required=False, label=_("Untagged VLAN VID"))
    tagged_vlan_vid = forms.IntegerField(required=False, label=_("Tagged VLAN VID"))
    qinq_svlan_vid = forms.IntegerField(required=False, label=_("Q-in-Q SVLAN VID"))
    vlan_translation_policy_id = DynamicModelMultipleChoiceField(
        queryset=VLANTranslationPolicy.objects.all(), required=False, label=_("VLAN translation policy")
    )
    poe_mode = forms.MultipleChoiceField(choices=InterfacePoEModeChoices, required=False, label=_("PoE mode"))
    poe_type = forms.MultipleChoiceField(choices=InterfacePoETypeChoices, required=False, label=_("PoE type"))
