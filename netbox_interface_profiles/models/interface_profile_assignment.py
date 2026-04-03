"""
InterfaceProfileAssignment model for netbox interface profiles.
"""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


class InterfaceProfileAssignment(NetBoxModel):
    """
    Links a single dcim.Interface to an InterfaceProfile.

    The relationship is many-to-one: many interfaces can be assigned to the
    same InterfaceProfile, but each interface can only have one assignment.
    """

    interface = models.OneToOneField(to="dcim.Interface", related_name="profile_assignment", on_delete=models.CASCADE)
    interface_profile = models.ForeignKey(
        to="netbox_interface_profiles.InterfaceProfile",
        on_delete=models.PROTECT,
        related_name="interface_assignments",
    )

    class Meta:
        ordering = ("interface",)
        verbose_name = "Interface Profile Assignment"
        verbose_name_plural = "Interface Profile Assignments"

    def __str__(self) -> str:
        return f"{self.interface} → {self.interface_profile}"

    def get_absolute_url(self) -> str:
        return reverse(
            "plugins:netbox_interface_profiles:interfaceprofileassignment",
            args=[self.pk],
        )
