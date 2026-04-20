"""
InterfaceTemplate model for netbox interface profiles.
"""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


class InterfaceTemplate(NetBoxModel):
    """
    An interface template that supports various NetBox interface attributes,
    scoped optionally to a SiteGroup. VLANs are referenced by VID to enable
    reusability across different sites with different VLAN objects but similar VIDs.

    This model enables templating of interface configurations that can be
    applied to multiple interfaces within a site/site group context.
    """

    # Configuration scope
    interface_profile = models.ForeignKey(
        to="netbox_interface_profiles.InterfaceProfile",
        on_delete=models.CASCADE,
        related_name="interface_templates",
    )
    scope_type = models.ForeignKey(to="contenttypes.ContentType", on_delete=models.CASCADE, blank=True, null=True)
    scope_id = models.PositiveBigIntegerField(blank=True, null=True)
    scope = GenericForeignKey(ct_field="scope_type", fk_field="scope_id")

    # Template identification
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Interface attributes - Physical
    speed = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Interface speed in Mbps (e.g., 1000, 10000)",
    )
    duplex = models.CharField(
        max_length=10,
        choices=(
            ("auto", "Auto"),
            ("half", "Half"),
            ("full", "Full"),
        ),
        null=True,
        blank=True,
    )
    mtu = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum transmission unit in bytes",
    )

    # Interface attributes - L2
    mode = models.CharField(
        max_length=20,
        choices=(
            ("access", "Access"),
            ("tagged", "Tagged"),
            ("tagged-all", "Tagged All"),
        ),
        null=True,
        blank=True,
        help_text="Interface mode (access/tagged/tagged-all)",
    )

    # Interface attributes - Status & Other
    enabled = models.BooleanField(
        default=True,
        help_text="Whether the interface is enabled by default",
    )
    poe_mode = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="POE mode (power-supply, power-device, etc.)",
    )

    # VLAN references (by VID for cross-site reusability)
    untagged_vlan_vid = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Untagged VLAN ID (VID). Will be resolved to actual VLAN in target site.",
    )
    tagged_vlans_vids = models.JSONField(
        default=list,
        blank=True,
        help_text="List of tagged VLAN IDs (VIDs) as JSON array. Will be resolved to actual VLANs in target site.",
    )

    class Meta:
        ordering = ("interface_profile", "name")
        verbose_name = "Interface Template"
        verbose_name_plural = "Interface Templates"
        constraints = [
            models.UniqueConstraint(
                fields=("interface_profile", "name"),
                name="unique_template_name_per_profile",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.interface_profile.name} → {self.name}"

    def get_absolute_url(self) -> str:
        return reverse("plugins:netbox_interface_profiles:interfacetemplate", args=[self.pk])

    def resolve_untagged_vlan(self, site):
        """Resolve untagged VLAN object for the provided site using the stored VID."""
        from ..utils import resolve_vlan_by_vid

        return resolve_vlan_by_vid(site=site, vid=self.untagged_vlan_vid)

    def resolve_tagged_vlans(self, site):
        """Resolve tagged VLAN objects for the provided site using stored VIDs."""
        from ..utils import resolve_vlans_by_vids

        return resolve_vlans_by_vids(site=site, vids=self.tagged_vlans_vids)
