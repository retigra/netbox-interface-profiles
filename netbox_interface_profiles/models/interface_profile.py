"""
InterfaceProfile model for netbox interface profiles.
"""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


class InterfaceProfile(NetBoxModel):
    """
    Represents a named interface configuration profile with an optional description.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Interface Profile"
        verbose_name_plural = "Interface Profiles"

    def __str__(self) -> str:
        return str(self.name)

    def get_absolute_url(self) -> str:
        return reverse("plugins:netbox_interface_profiles:interfaceprofile", args=[self.pk])
