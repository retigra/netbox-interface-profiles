"""
Object actions for netbox interface profiles.

These render as bulk action buttons beneath the Device 'Interface Roles' table and submit
the selected interfaces to DeviceInterfaceRoleTabView.post().
"""

from django.utils.translation import gettext_lazy as _
from netbox.object_actions import ObjectAction

from .forms import DeviceBulkAssignRoleForm
from .permissions import restrict_assignable_roles

__all__ = (
    "BulkAssignInterfaceRole",
    "BulkRemoveInterfaceRole",
)


class InterfaceRoleAssignmentAction(ObjectAction):
    """
    Base for bulk actions on the interface role assignments of the selected interfaces.

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


class BulkAssignInterfaceRole(InterfaceRoleAssignmentAction):
    name = "bulk_assign_interface_role"
    label = _("Assign Role")
    template_name = "netbox_interface_profiles/buttons/bulk_assign_role.html"
    assignment_permissions = (
        "netbox_interface_profiles.add_interfaceroleassignment",
        "netbox_interface_profiles.change_interfaceroleassignment",
    )

    @classmethod
    def get_context(cls, context, obj):
        form = DeviceBulkAssignRoleForm(device=context["object"])
        return {
            "roles": restrict_assignable_roles(form.fields["interface_role"].queryset, context["request"].user),
        }


class BulkRemoveInterfaceRole(InterfaceRoleAssignmentAction):
    name = "bulk_remove_interface_role"
    label = _("Remove Role")
    template_name = "netbox_interface_profiles/buttons/bulk_remove_role.html"
    assignment_permissions = ("netbox_interface_profiles.delete_interfaceroleassignment",)
