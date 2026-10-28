"""
ProfileConfigTemplate model for netbox interface profiles.
"""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


class ProfileConfigTemplate(NetBoxModel):
    """
    A Jinja2 configuration template scoped to an InterfaceRole, a Platform,
    and an optional DeviceType.
    """

    interface_template = models.ForeignKey(
        to="netbox_interface_profiles.InterfaceTemplate",
        on_delete=models.CASCADE,
        related_name="config_templates",
    )
    platform = models.ForeignKey(
        to="dcim.Platform",
        on_delete=models.PROTECT,
        related_name="interface_profile_config_templates",
    )
    device_type = models.ForeignKey(
        to="dcim.DeviceType",
        on_delete=models.SET_NULL,
        related_name="interface_profile_config_templates",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    template_code = models.TextField(
        help_text="Jinja2 template code used to render the interface configuration.",
    )

    class Meta:
        ordering = ("interface_template", "platform", "name")
        verbose_name = "Profile Config Template"
        verbose_name_plural = "Profile Config Templates"

    def __str__(self) -> str:
        return f"{self.name}"

    def get_absolute_url(self) -> str:
        return reverse("plugins:netbox_interface_profiles:profileconfigtemplate", args=[self.pk])
