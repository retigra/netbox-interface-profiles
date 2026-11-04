"""
InterfaceRoleAssignment model for interface profiles.
"""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


class InterfaceRoleAssignment(NetBoxModel):
    """
    Links a single dcim.Interface to an InterfaceRole.

    The relationship is many-to-one: many interfaces can be assigned to the
    same InterfaceRole, but each interface can only have one assignment.
    """

    interface = models.OneToOneField(to="dcim.Interface", related_name="role_assignment", on_delete=models.CASCADE)
    interface_role = models.ForeignKey(
        to="interface_profiles.InterfaceRole",
        on_delete=models.PROTECT,
        related_name="interface_assignments",
    )

    class Meta:
        ordering = ("interface",)
        verbose_name = "Interface Role Assignment"
        verbose_name_plural = "Interface Role Assignments"

    def __str__(self) -> str:
        return f"{self.interface} → {self.interface_role}"

    def get_absolute_url(self) -> str:
        return reverse(
            "plugins:interface_profiles:interfaceroleassignment",
            args=[self.pk],
        )
