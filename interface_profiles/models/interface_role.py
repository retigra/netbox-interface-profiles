"""
InterfaceRole model for interface profiles.
"""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from netbox.models.features import JobsMixin


class InterfaceRole(JobsMixin, NetBoxModel):
    """
    Represents a named interface configuration role with an optional description.
    Can be scoped to one or more device roles to limit availability in assignment UI.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    group = models.ForeignKey(
        to="interface_profiles.RoleGroup",
        on_delete=models.SET_NULL,
        related_name="interface_roles",
        blank=True,
        null=True,
        help_text="Role group used to scope assignment permissions.",
    )
    device_roles = models.ManyToManyField(
        to="dcim.DeviceRole",
        blank=True,
        related_name="interface_roles",
        help_text="If specified, this role is only available for assignment to interfaces on devices with these device roles. If empty, role is available for all devices.",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Interface Role"
        verbose_name_plural = "Interface Roles"

    def __str__(self) -> str:
        return str(self.name)

    def get_absolute_url(self) -> str:
        return reverse("plugins:interface_profiles:interfacerole", args=[self.pk])
