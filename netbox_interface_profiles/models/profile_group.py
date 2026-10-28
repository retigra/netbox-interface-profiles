"""
ProfileGroup model for netbox interface profiles.
"""

from django.urls import reverse
from netbox.models import OrganizationalModel


class ProfileGroup(OrganizationalModel):
    """
    Groups interface profiles by operational impact (e.g. access ports vs. trunks).

    Groups carry no behaviour of their own; they exist so that NetBox object permissions can be
    constrained on them, e.g. `{"interface_profile__group__slug": "access"}` on Interface Profile
    Assignment to let service desk staff assign only access-port profiles.
    """

    class Meta:
        ordering = ("name",)
        verbose_name = "Profile Group"
        verbose_name_plural = "Profile Groups"

    def get_absolute_url(self) -> str:
        return reverse("plugins:netbox_interface_profiles:profilegroup", args=[self.pk])
