"""
RoleGroup model for netbox interface profiles.
"""

from django.urls import reverse
from netbox.models import OrganizationalModel


class RoleGroup(OrganizationalModel):
    """
    Groups interface roles by operational impact (e.g. access ports vs. trunks).

    Groups carry no behaviour of their own; they exist so that NetBox object permissions can be
    constrained on them, e.g. `{"interface_role__group__slug": "access"}` on Interface Role
    Assignment to let service desk staff assign only access-port roles.
    """

    class Meta:
        ordering = ("name",)
        verbose_name = "Role Group"
        verbose_name_plural = "Role Groups"

    def get_absolute_url(self) -> str:
        return reverse("plugins:netbox_interface_profiles:rolegroup", args=[self.pk])
