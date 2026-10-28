"""
Object actions for netbox interface profiles.

These render as bulk action buttons beneath the Device 'Interface Profiles' table and submit
the selected interfaces to DeviceInterfaceProfileTabView.post().
"""

from django.utils.translation import gettext_lazy as _
from netbox.object_actions import ObjectAction

from .forms import DeviceBulkAssignProfileForm
from .permissions import restrict_assignable_profiles

__all__ = (
    "BulkAssignInterfaceProfile",
    "BulkRemoveInterfaceProfile",
)


class InterfaceProfileAssignmentAction(ObjectAction):
    """
    Base for bulk actions on the interface profile assignments of the selected interfaces.

    NetBox checks `permissions_required` against the table's model (Interface), so the
    assignment permissions these actions need are declared separately in
    `assignment_permissions` and enforced by the view.
    """

    multi = True
    assignment_permissions = ()

    @classmethod
    def get_url(cls, obj):
        # Submit to the form's own URL (the device tab view) rather than a separate view
        return None


class BulkAssignInterfaceProfile(InterfaceProfileAssignmentAction):
    name = "bulk_assign_interface_profile"
    label = _("Assign Profile")
    template_name = "netbox_interface_profiles/buttons/bulk_assign_profile.html"
    assignment_permissions = (
        "netbox_interface_profiles.add_interfaceprofileassignment",
        "netbox_interface_profiles.change_interfaceprofileassignment",
    )

    @classmethod
    def get_context(cls, context, obj):
        form = DeviceBulkAssignProfileForm(device=context["object"])
        return {
            "profiles": restrict_assignable_profiles(
                form.fields["interface_profile"].queryset, context["request"].user
            ),
        }


class BulkRemoveInterfaceProfile(InterfaceProfileAssignmentAction):
    name = "bulk_remove_interface_profile"
    label = _("Remove Profile")
    template_name = "netbox_interface_profiles/buttons/bulk_remove_profile.html"
    assignment_permissions = ("netbox_interface_profiles.delete_interfaceprofileassignment",)
