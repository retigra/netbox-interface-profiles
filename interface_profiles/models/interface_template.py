"""
InterfaceTemplate model for interface profiles.
"""

from typing import Any, cast

from dcim.choices import InterfaceDuplexChoices, InterfaceModeChoices, InterfacePoEModeChoices, InterfacePoETypeChoices
from dcim.constants import INTERFACE_MTU_MAX, INTERFACE_MTU_MIN
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from ipam.constants import VLAN_VID_MAX, VLAN_VID_MIN
from netbox.models import NetBoxModel

# Template fields applied to the interface, mapped to the interface field they set. VLANs are resolved separately.
TEMPLATE_INTERFACE_FIELDS = {
    "enabled": "enabled",
    "mgmt_only": "mgmt_only",
    "interface_description": "description",
    "speed": "speed",
    "duplex": "duplex",
    "mtu": "mtu",
    "mode": "mode",
    "poe_mode": "poe_mode",
    "poe_type": "poe_type",
    "vrf": "vrf",
    "vlan_translation_policy": "vlan_translation_policy",
}

# Template fields that are skipped by synchronization when empty, unless their set_null_<field> flag is enabled
NULLABLE_TEMPLATE_FIELDS = (
    "interface_description",
    "speed",
    "duplex",
    "mtu",
    "mode",
    "poe_mode",
    "poe_type",
    "vrf",
    "vlan_translation_policy",
    "untagged_vlan_vid",
    "qinq_svlan_vid",
)

# The relation holding the objects in scope, by the model of the scope type
SCOPE_RELATIONS = {
    "site": "scope_sites",
    "sitegroup": "scope_site_groups",
}

VID_VALIDATORS = (MinValueValidator(VLAN_VID_MIN), MaxValueValidator(VLAN_VID_MAX))


def _set_null_field(verbose_name: str, help_text: str):
    return models.BooleanField(default=False, verbose_name=verbose_name, help_text=help_text)


class InterfaceTemplate(NetBoxModel):
    """
    The interface attributes an InterfaceRole applies, globally or scoped to Sites or SiteGroups.

    The scope type selects which of the scope relations holds the scope, the other one is always empty. A template
    without a scope type is global.

    Empty attributes leave the interface unchanged, unless their set_null_<field> flag is enabled. VLANs are
    referenced by VID, so one template works in every site even though each site has its own VLAN objects.
    """

    # Configuration scope
    interface_role = models.ForeignKey(
        to="interface_profiles.InterfaceRole",
        on_delete=models.CASCADE,
        related_name="interface_templates",
    )
    scope_type = models.ForeignKey(to="contenttypes.ContentType", on_delete=models.CASCADE, blank=True, null=True)
    scope_sites = models.ManyToManyField(
        to="dcim.Site",
        related_name="interface_role_templates",
        blank=True,
        verbose_name="Sites",
    )
    scope_site_groups = models.ManyToManyField(
        to="dcim.SiteGroup",
        related_name="interface_role_templates",
        blank=True,
        verbose_name="Site groups",
    )

    # Template identification
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Interface attributes - General
    enabled = models.BooleanField(
        default=True,
        help_text="Whether the interface is enabled. Always applied.",
    )
    mgmt_only = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Management only",
        help_text="Whether the interface is used only for out-of-band management. Empty leaves it unchanged.",
    )
    interface_description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Interface description",
        help_text="Description set on the interface",
    )

    # Interface attributes - Physical
    speed = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Speed (Kbps)",
    )
    duplex = models.CharField(
        max_length=50,
        choices=InterfaceDuplexChoices,
        null=True,
        blank=True,
    )
    mtu = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(INTERFACE_MTU_MIN), MaxValueValidator(INTERFACE_MTU_MAX)],
        verbose_name="MTU",
    )

    # Interface attributes - PoE
    poe_mode = models.CharField(
        max_length=50,
        choices=InterfacePoEModeChoices,
        null=True,
        blank=True,
        verbose_name="PoE mode",
    )
    poe_type = models.CharField(
        max_length=50,
        choices=InterfacePoETypeChoices,
        null=True,
        blank=True,
        verbose_name="PoE type",
    )

    # Interface attributes - Addressing
    vrf = models.ForeignKey(
        to="ipam.VRF",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="VRF",
    )

    # Interface attributes - 802.1Q switching
    mode = models.CharField(
        max_length=50,
        choices=InterfaceModeChoices,
        null=True,
        blank=True,
        verbose_name="802.1Q mode",
    )
    # VLANs are referenced by VID for cross-site reusability
    untagged_vlan_vid = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=VID_VALIDATORS,
        verbose_name="Untagged VLAN VID",
        help_text="Resolved to the VLAN with this VID in the site of the interface.",
    )
    tagged_vlans_vids = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Tagged VLAN VIDs",
        help_text="Resolved to the VLANs with these VIDs in the site of the interface. Requires the tagged mode.",
    )
    qinq_svlan_vid = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=VID_VALIDATORS,
        verbose_name="Q-in-Q SVLAN VID",
        help_text="Resolved to the service VLAN with this VID in the site of the interface. Requires the Q-in-Q mode.",
    )
    vlan_translation_policy = models.ForeignKey(
        to="ipam.VLANTranslationPolicy",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="VLAN translation policy",
    )

    # Explicitly clear interface attributes, as an empty value leaves the interface unchanged
    set_null_interface_description = _set_null_field(
        "Clear interface description", "Clear the interface description when no interface description is set"
    )
    set_null_speed = _set_null_field("Clear speed", "Clear the interface speed when no speed is set")
    set_null_duplex = _set_null_field("Clear duplex", "Clear the interface duplex when no duplex is set")
    set_null_mtu = _set_null_field("Clear MTU", "Clear the interface MTU when no MTU is set")
    set_null_mode = _set_null_field(
        "Clear mode", "Clear the interface mode when no mode is set. This also removes all VLAN assignments."
    )
    set_null_poe_mode = _set_null_field("Clear PoE mode", "Clear the interface PoE mode when no PoE mode is set")
    set_null_poe_type = _set_null_field("Clear PoE type", "Clear the interface PoE type when no PoE type is set")
    set_null_vrf = _set_null_field("Clear VRF", "Clear the interface VRF when no VRF is set")
    set_null_vlan_translation_policy = _set_null_field(
        "Clear VLAN translation policy",
        "Clear the interface VLAN translation policy when no VLAN translation policy is set",
    )
    set_null_untagged_vlan_vid = _set_null_field(
        "Clear untagged VLAN", "Clear the interface untagged VLAN when no untagged VLAN VID is set"
    )
    set_null_qinq_svlan_vid = _set_null_field(
        "Clear Q-in-Q SVLAN", "Clear the interface Q-in-Q service VLAN when no SVLAN VID is set"
    )

    class Meta:
        ordering = ("interface_role", "name")
        verbose_name = "Interface Template"
        verbose_name_plural = "Interface Templates"
        constraints = [
            models.UniqueConstraint(
                fields=("interface_role", "name"),
                name="unique_template_name_per_role",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.interface_role.name} → {self.name}"

    def get_absolute_url(self) -> str:
        return reverse("plugins:interface_profiles:interfacetemplate", args=[self.pk])

    def clean(self):
        super().clean()

        errors: dict[str, str] = {}

        if scope_error := self._clean_scope():
            errors[NON_FIELD_ERRORS] = scope_error

        vids = self.tagged_vlans_vids
        if not isinstance(vids, list) or not all(
            isinstance(vid, int) and VLAN_VID_MIN <= vid <= VLAN_VID_MAX for vid in vids
        ):
            errors["tagged_vlans_vids"] = f"Enter a list of VIDs between {VLAN_VID_MIN} and {VLAN_VID_MAX}."

        for field in NULLABLE_TEMPLATE_FIELDS:
            if getattr(self, f"set_null_{field}") and self._has_value(field):
                errors[f"set_null_{field}"] = "Remove the value to clear this attribute."

        if self.set_null_mode and (self.untagged_vlan_vid is not None or self.tagged_vlans_vids or self.qinq_svlan_vid):
            errors.setdefault("set_null_mode", "VLANs cannot be assigned to an interface without a mode.")
        if self.mode and self.mode != InterfaceModeChoices.MODE_TAGGED and self.tagged_vlans_vids:
            errors.setdefault("tagged_vlans_vids", "Tagged VLANs can only be assigned in the tagged mode.")
        if self.mode and self.mode != InterfaceModeChoices.MODE_Q_IN_Q and self.qinq_svlan_vid is not None:
            errors.setdefault("qinq_svlan_vid", "A service VLAN can only be assigned in the Q-in-Q mode.")

        if errors:
            raise ValidationError(errors)

    def _scope_relation_pks(self, relation: str) -> list[int]:
        """Return the primary keys of a scope relation, preferring the values being saved by a form or the API."""
        m2m_values = getattr(self, "_m2m_values", {})
        if relation in m2m_values:
            return [getattr(value, "pk", value) for value in m2m_values[relation]]
        if self.pk:
            return list(getattr(self, relation).values_list("pk", flat=True))
        return []

    def _clean_scope(self) -> str | None:
        """Validate the objects in scope like NetBox validates the scope of a VLAN group, for multiple objects."""
        selected = {relation: self._scope_relation_pks(relation) for relation in SCOPE_RELATIONS.values()}
        if self.scope_type is None:
            return "Please select a scope type." if any(selected.values()) else None

        model = self.scope_type.model_class()
        for relation, pks in selected.items():
            if relation != self.scope_relation and pks:
                return (
                    f"{cast(Any, self)._meta.get_field(relation).verbose_name} cannot be selected for a "
                    f"{model._meta.verbose_name} scope."
                )
        if not selected.get(self.scope_relation):
            return f"Please select a {model._meta.verbose_name}."
        return None

    @property
    def scope_relation(self) -> str | None:
        """Name of the relation holding the objects in scope, or None for a global template."""
        return SCOPE_RELATIONS.get(self.scope_type.model) if self.scope_type else None

    @property
    def scope_objects(self):
        """The sites or site groups in scope, or None for a global template."""
        relation = self.scope_relation
        return getattr(self, relation).all() if relation else None

    @property
    def scope_ids(self) -> list[int]:
        """IDs of the sites or site groups in scope."""
        scopes = self.scope_objects
        return [scope.pk for scope in scopes] if scopes is not None else []

    def _has_value(self, field: str) -> bool:
        return getattr(self, cast(Any, self)._meta.get_field(field).attname) not in (None, "")

    def is_set_null(self, field: str) -> bool:
        """Return whether synchronization should clear the interface attribute for an empty template field."""
        return field in NULLABLE_TEMPLATE_FIELDS and getattr(self, f"set_null_{field}")

    def resolve_untagged_vlan(self, site):
        """Resolve untagged VLAN object for the provided site using the stored VID."""
        from ..utils import resolve_vlan_by_vid

        return resolve_vlan_by_vid(site=site, vid=cast(int | None, self.untagged_vlan_vid))

    def resolve_tagged_vlans(self, site):
        """Resolve tagged VLAN objects for the provided site using stored VIDs."""
        from ..utils import resolve_vlans_by_vids

        return resolve_vlans_by_vids(site=site, vids=cast(list[int], self.tagged_vlans_vids))

    def resolve_qinq_svlan(self, site):
        """Resolve the Q-in-Q service VLAN object for the provided site using the stored VID."""
        from ipam.choices import VLANQinQRoleChoices

        from ..utils import resolve_vlan_by_vid

        return resolve_vlan_by_vid(
            site=site,
            vid=cast(int | None, self.qinq_svlan_vid),
            qinq_role=VLANQinQRoleChoices.ROLE_SERVICE,
        )
