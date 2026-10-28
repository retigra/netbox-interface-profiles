"""
InterfaceProfile model for netbox interface profiles.
"""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from netbox.models.features import JobsMixin


class InterfaceProfile(JobsMixin, NetBoxModel):
    """
    Represents a named interface configuration profile with an optional description.
    Can be scoped to one or more device roles to limit availability in assignment UI.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    group = models.ForeignKey(
        to="netbox_interface_profiles.ProfileGroup",
        on_delete=models.SET_NULL,
        related_name="interface_profiles",
        blank=True,
        null=True,
        help_text="Profile group used to scope assignment permissions.",
    )
    device_roles = models.ManyToManyField(
        to="dcim.DeviceRole",
        blank=True,
        related_name="interface_profiles",
        help_text="If specified, this profile is only available for assignment to interfaces on devices with these roles. If empty, profile is available for all devices.",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Interface Profile"
        verbose_name_plural = "Interface Profiles"

    def __str__(self) -> str:
        return str(self.name)

    def get_absolute_url(self) -> str:
        return reverse("plugins:netbox_interface_profiles:interfaceprofile", args=[self.pk])
