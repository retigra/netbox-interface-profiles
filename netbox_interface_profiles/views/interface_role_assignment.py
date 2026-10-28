"""
InterfaceRoleAssignment views for netbox interface profiles.
"""

from dcim.filtersets import InterfaceFilterSet
from dcim.forms import InterfaceFilterForm
from dcim.models import Device, Interface
from dcim.object_actions import BulkDisconnect
from dcim.views import DeviceComponentsView
from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch, Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from ipam.models import IPAddress
from netbox.object_actions import BulkDelete, BulkEdit, BulkRename, DeleteObject, EditObject
from netbox.views import generic
from utilities.exceptions import AbortRequest, PermissionsViolation
from utilities.views import ViewTab, register_model_view

from .. import filtersets, forms, models, tables
from ..object_actions import BulkAssignInterfaceRole, BulkRemoveInterfaceRole
from ..permissions import assign_role, restrict_assignable_roles

# ---------------------------------------------------------------------------
# InterfaceRoleAssignment CRUD views
# ---------------------------------------------------------------------------


class InterfaceRoleAssignmentView(generic.ObjectView):
    queryset = models.InterfaceRoleAssignment.objects.select_related("interface__device", "interface_role")


class InterfaceRoleAssignmentListView(generic.ObjectListView):
    queryset = models.InterfaceRoleAssignment.objects.select_related("interface__device", "interface_role")
    table = tables.InterfaceRoleAssignmentTable
    filterset = filtersets.InterfaceRoleAssignmentFilterSet
    filterset_form = forms.InterfaceRoleAssignmentFilterSetForm


class InterfaceRoleAssignmentEditView(generic.ObjectEditView):
    queryset = models.InterfaceRoleAssignment.objects.all()
    form = forms.InterfaceRoleAssignmentForm


class InterfaceRoleAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = models.InterfaceRoleAssignment.objects.all()


class InterfaceRoleAssignmentBulkImportView(generic.BulkImportView):
    queryset = models.InterfaceRoleAssignment.objects.all()
    model_form = forms.InterfaceRoleAssignmentImportForm
    table = tables.InterfaceRoleAssignmentTable


class InterfaceRoleAssignmentBulkEditView(generic.BulkEditView):
    queryset = models.InterfaceRoleAssignment.objects.all()
    filterset = filtersets.InterfaceRoleAssignmentFilterSet
    table = tables.InterfaceRoleAssignmentTable
    form = forms.InterfaceRoleAssignmentBulkEditForm


class InterfaceRoleAssignmentBulkDeleteView(generic.BulkDeleteView):
    queryset = models.InterfaceRoleAssignment.objects.all()
    filterset = filtersets.InterfaceRoleAssignmentFilterSet
    table = tables.InterfaceRoleAssignmentTable


# ---------------------------------------------------------------------------
# Device tab
# ---------------------------------------------------------------------------


def _get_devices_for_virtual_chassis(device):
    """
    Get the device and any virtual chassis member devices if device is a master.

    Args:
        device: A Device instance

    Returns:
        QuerySet of Device objects (the device itself plus any members if it's a VC master)
    """
    devices = Device.objects.filter(pk=device.pk)

    # If device is a virtual chassis master, include all member devices
    if device.virtual_chassis and device.virtual_chassis.master == device:
        members = device.virtual_chassis.members.all()
        devices = devices | members

    return devices


@register_model_view(Device, name="interface_roles", path="interface-roles")
class DeviceInterfaceRoleTabView(DeviceComponentsView):
    """Tab on the Device detail page showing all interfaces with their assigned role."""

    queryset = Device.objects.all()
    child_model = Interface
    table = tables.DeviceInterfaceTable
    filterset = InterfaceFilterSet
    filterset_form = InterfaceFilterForm
    actions = (
        EditObject,
        DeleteObject,
        BulkEdit,
        BulkRename,
        BulkDisconnect,
        BulkDelete,
        BulkAssignInterfaceRole,
        BulkRemoveInterfaceRole,
    )
    template_name = "netbox_interface_profiles/device_interface_roles_tab.html"
    tab = ViewTab(
        label="Interface Roles",
        badge=lambda obj: Interface.objects.filter(device__in=_get_devices_for_virtual_chassis(obj)).count(),
        permission="netbox_interface_profiles.view_interfaceroleassignment",
    )

    def get_permitted_actions(self, user, model=None):
        # Role actions are permitted on InterfaceRoleAssignment, not on the table's Interface model
        return [
            action
            for action in super().get_permitted_actions(user, model)
            if user.has_perms(getattr(action, "assignment_permissions", ()))
        ]

    def get_children(self, request, parent):
        devices = _get_devices_for_virtual_chassis(parent)
        return (
            Interface.objects.restrict(request.user, "view")
            .filter(device__in=devices)
            .select_related("role_assignment__interface_role")
            .prefetch_related(
                Prefetch("ip_addresses", queryset=IPAddress.objects.restrict(request.user)),
                Prefetch("member_interfaces", queryset=Interface.objects.restrict(request.user)),
            )
            .order_by("device__name", "name")
        )

    def post(self, request, **kwargs):
        device = get_object_or_404(self.queryset, **kwargs)
        return_url = request.get_full_path()
        selected_pks = request.POST.getlist("pk")

        if not selected_pks:
            messages.warning(request, _("No interfaces selected."))
            return redirect(return_url)

        devices = _get_devices_for_virtual_chassis(device)
        interfaces = Interface.objects.restrict(request.user, "view").filter(device__in=devices, pk__in=selected_pks)

        if "_assign" in request.POST:
            if not request.user.has_perms(BulkAssignInterfaceRole.assignment_permissions):
                return HttpResponseForbidden()

            assign_form = forms.DeviceBulkAssignRoleForm(
                device=device,
                data={"interface_role": request.POST.get("_assign")},
            )
            role = assign_form.cleaned_data["interface_role"] if assign_form.is_valid() else None
            if not role:
                messages.error(request, _("Please select a valid Interface Role."))
                return redirect(return_url)

            created = updated = 0
            try:
                with transaction.atomic():
                    for iface in interfaces:
                        _assignment, was_created = assign_role(request.user, iface, role)
                        if was_created:
                            created += 1
                        else:
                            updated += 1
            except PermissionsViolation:
                messages.error(
                    request,
                    _("You are not permitted to assign {role} to {interface}. No changes were made.").format(
                        role=role, interface=iface
                    ),
                )
                return redirect(return_url)
            except AbortRequest as exc:
                messages.error(request, _("{error} No changes were made.").format(error=exc.message))
                return redirect(return_url)
            if created:
                messages.success(
                    request, _("Assigned {role} to {count} interface(s).").format(role=role, count=created)
                )
            if updated:
                messages.success(request, _("Updated {count} interface(s) to {role}.").format(role=role, count=updated))

        elif "_remove" in request.POST:
            if not request.user.has_perms(BulkRemoveInterfaceRole.assignment_permissions):
                return HttpResponseForbidden()

            assignments = list(
                models.InterfaceRoleAssignment.objects.restrict(request.user, "delete")
                .select_related("interface", "interface_role")
                .filter(interface__in=interfaces)
            )
            with transaction.atomic():
                for assignment in assignments:
                    assignment.delete()
            messages.success(request, _("Removed {count} role assignment(s).").format(count=len(assignments)))

            skipped = models.InterfaceRoleAssignment.objects.filter(interface__in=interfaces).count()
            if skipped:
                messages.warning(
                    request,
                    _("Skipped {count} assignment(s) you are not permitted to remove.").format(count=skipped),
                )

        return redirect(return_url)


def _get_applicable_roles(interface: Interface):
    """
    Return roles applicable to an interface.

    Filters by:
    1. Config template scope (if role has config templates, see ProfileConfigTemplate.objects.in_scope())
    2. Device role restrictions (if role has device_roles set)
    """
    device = interface.device
    config_templates = models.ProfileConfigTemplate.objects.all()

    # Roles without config templates are unrestricted, others need a config template in scope
    roles = models.InterfaceRole.objects.filter(
        ~Q(pk__in=config_templates.values("interface_role"))
        | Q(pk__in=config_templates.in_scope(interface).values("interface_role"))
    )

    if device.role_id:
        roles = roles.filter(Q(device_roles__isnull=True) | Q(device_roles=device.role_id)).distinct()
    else:
        roles = roles.filter(device_roles__isnull=True)

    return roles.order_by("name")


class InterfaceRoleAssignmentMenuHTMXView(View):
    """Render HTMX dropdown menu items for a single interface row."""

    def get(self, request, interface_id: int):
        if not request.user.has_perm("netbox_interface_profiles.view_interfaceroleassignment"):
            return HttpResponseForbidden()

        interface = get_object_or_404(
            Interface.objects.restrict(request.user, "view").select_related(
                "device__platform",
                "device__device_type",
                "role_assignment__interface_role",
            ),
            pk=interface_id,
        )

        roles = _get_applicable_roles(interface)
        assignment = getattr(interface, "role_assignment", None)
        current_role = getattr(assignment, "interface_role", None)

        if current_role and not roles.filter(pk=current_role.pk).exists():
            roles = models.InterfaceRole.objects.filter(Q(pk__in=roles.values("pk")) | Q(pk=current_role.pk)).order_by(
                "name"
            )

        # Roles outside the user's permissions are listed but disabled, so it is clear they exist
        assignable_role_ids = set(
            restrict_assignable_roles(roles, request.user, interface).values_list("pk", flat=True)
        )
        can_clear = (
            assignment is not None
            and models.InterfaceRoleAssignment.objects.restrict(request.user, "delete")
            .filter(pk=assignment.pk)
            .exists()
        )

        return render(
            request,
            "netbox_interface_profiles/inc/interface_role_menu_items.html",
            {
                "interface": interface,
                "roles": roles,
                "current_role": current_role,
                "assignable_role_ids": assignable_role_ids,
                "can_clear": can_clear,
            },
        )


class InterfaceRoleAssignmentSetHTMXView(View):
    """Assign a role to an interface via HTMX."""

    def post(self, request, interface_id: int, role_id: int):
        can_add = request.user.has_perm("netbox_interface_profiles.add_interfaceroleassignment")
        can_change = request.user.has_perm("netbox_interface_profiles.change_interfaceroleassignment")
        if not (can_add or can_change):
            return HttpResponseForbidden()

        interface = get_object_or_404(Interface.objects.restrict(request.user, "view"), pk=interface_id)
        role = get_object_or_404(models.InterfaceRole.objects.all(), pk=role_id)

        try:
            assign_role(request.user, interface, role)
        except PermissionsViolation:
            # A plain 403 is swallowed by HTMX; refresh so the message is shown instead
            messages.error(
                request,
                _("You are not permitted to assign {role} to {interface}.").format(role=role, interface=interface),
            )
        except AbortRequest as exc:
            messages.error(request, exc.message)
        return HttpResponse(status=204, headers={"HX-Refresh": "true"})


class InterfaceRoleAssignmentRemoveHTMXView(View):
    """Remove a role assignment from an interface via HTMX."""

    def post(self, request, interface_id: int):
        if not request.user.has_perm("netbox_interface_profiles.delete_interfaceroleassignment"):
            return HttpResponseForbidden()

        assignment = (
            models.InterfaceRoleAssignment.objects.select_related("interface", "interface_role")
            .filter(interface_id=interface_id)
            .first()
        )
        if assignment is None:
            return HttpResponse(status=204, headers={"HX-Refresh": "true"})

        if models.InterfaceRoleAssignment.objects.restrict(request.user, "delete").filter(pk=assignment.pk).exists():
            assignment.delete()
        else:
            messages.error(
                request,
                _("You are not permitted to remove {role} from {interface}.").format(
                    role=assignment.interface_role, interface=assignment.interface
                ),
            )
        return HttpResponse(status=204, headers={"HX-Refresh": "true"})
