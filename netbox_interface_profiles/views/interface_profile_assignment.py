"""
InterfaceProfileAssignment views for netbox interface profiles.
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
from ..object_actions import BulkAssignInterfaceProfile, BulkRemoveInterfaceProfile
from ..permissions import assign_profile, restrict_assignable_profiles

# ---------------------------------------------------------------------------
# InterfaceProfileAssignment CRUD views
# ---------------------------------------------------------------------------


class InterfaceProfileAssignmentView(generic.ObjectView):
    queryset = models.InterfaceProfileAssignment.objects.select_related("interface__device", "interface_profile")


class InterfaceProfileAssignmentListView(generic.ObjectListView):
    queryset = models.InterfaceProfileAssignment.objects.select_related("interface__device", "interface_profile")
    table = tables.InterfaceProfileAssignmentTable
    filterset = filtersets.InterfaceProfileAssignmentFilterSet
    filterset_form = forms.InterfaceProfileAssignmentFilterSetForm


class InterfaceProfileAssignmentEditView(generic.ObjectEditView):
    queryset = models.InterfaceProfileAssignment.objects.all()
    form = forms.InterfaceProfileAssignmentForm


class InterfaceProfileAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = models.InterfaceProfileAssignment.objects.all()


class InterfaceProfileAssignmentBulkImportView(generic.BulkImportView):
    queryset = models.InterfaceProfileAssignment.objects.all()
    model_form = forms.InterfaceProfileAssignmentImportForm
    table = tables.InterfaceProfileAssignmentTable


class InterfaceProfileAssignmentBulkEditView(generic.BulkEditView):
    queryset = models.InterfaceProfileAssignment.objects.all()
    filterset = filtersets.InterfaceProfileAssignmentFilterSet
    table = tables.InterfaceProfileAssignmentTable
    form = forms.InterfaceProfileAssignmentBulkEditForm


class InterfaceProfileAssignmentBulkDeleteView(generic.BulkDeleteView):
    queryset = models.InterfaceProfileAssignment.objects.all()
    filterset = filtersets.InterfaceProfileAssignmentFilterSet
    table = tables.InterfaceProfileAssignmentTable


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


@register_model_view(Device, name="interface_profiles", path="interface-profiles")
class DeviceInterfaceProfileTabView(DeviceComponentsView):
    """Tab on the Device detail page showing all interfaces with their assigned profile."""

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
        BulkAssignInterfaceProfile,
        BulkRemoveInterfaceProfile,
    )
    template_name = "netbox_interface_profiles/device_interface_profiles_tab.html"
    tab = ViewTab(
        label="Interface Profiles",
        badge=lambda obj: Interface.objects.filter(device__in=_get_devices_for_virtual_chassis(obj)).count(),
        permission="netbox_interface_profiles.view_interfaceprofileassignment",
    )

    def get_permitted_actions(self, user, model=None):
        # Profile actions are permitted on InterfaceProfileAssignment, not on the table's Interface model
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
            .select_related("profile_assignment__interface_profile")
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
            if not request.user.has_perms(BulkAssignInterfaceProfile.assignment_permissions):
                return HttpResponseForbidden()

            assign_form = forms.DeviceBulkAssignProfileForm(
                device=device,
                data={"interface_profile": request.POST.get("_assign")},
            )
            profile = assign_form.cleaned_data["interface_profile"] if assign_form.is_valid() else None
            if not profile:
                messages.error(request, _("Please select a valid Interface Profile."))
                return redirect(return_url)

            created = updated = 0
            try:
                with transaction.atomic():
                    for iface in interfaces:
                        _assignment, was_created = assign_profile(request.user, iface, profile)
                        if was_created:
                            created += 1
                        else:
                            updated += 1
            except PermissionsViolation:
                messages.error(
                    request,
                    _("You are not permitted to assign {profile} to {interface}. No changes were made.").format(
                        profile=profile, interface=iface
                    ),
                )
                return redirect(return_url)
            except AbortRequest as exc:
                messages.error(request, _("{error} No changes were made.").format(error=exc.message))
                return redirect(return_url)
            if created:
                messages.success(
                    request, _("Assigned {profile} to {count} interface(s).").format(profile=profile, count=created)
                )
            if updated:
                messages.success(
                    request, _("Updated {count} interface(s) to {profile}.").format(profile=profile, count=updated)
                )

        elif "_remove" in request.POST:
            if not request.user.has_perms(BulkRemoveInterfaceProfile.assignment_permissions):
                return HttpResponseForbidden()

            assignments = list(
                models.InterfaceProfileAssignment.objects.restrict(request.user, "delete")
                .select_related("interface", "interface_profile")
                .filter(interface__in=interfaces)
            )
            with transaction.atomic():
                for assignment in assignments:
                    assignment.delete()
            messages.success(request, _("Removed {count} profile assignment(s).").format(count=len(assignments)))

            skipped = models.InterfaceProfileAssignment.objects.filter(interface__in=interfaces).count()
            if skipped:
                messages.warning(
                    request,
                    _("Skipped {count} assignment(s) you are not permitted to remove.").format(count=skipped),
                )

        return redirect(return_url)


def _get_applicable_profiles(device: Device):
    """
    Return profiles applicable to a device.

    Filters by:
    1. Config template scope (platform + device_type)
    2. Device role restrictions (if profile has device_roles set)
    """
    if device.platform is None:
        # No platform: return profiles without device role if device has no role,
        # or with matching device role if device has one
        if device.role:
            return (
                models.InterfaceProfile.objects.filter(Q(device_roles__isnull=True) | Q(device_roles=device.role))
                .distinct()
                .order_by("name")
            )
        else:
            return models.InterfaceProfile.objects.filter(device_roles__isnull=True).order_by("name")

    # Has platform: filter by config template scope first
    profiles = (
        models.InterfaceProfile.objects.filter(
            interface_templates__config_templates__platform=device.platform,
        )
        .filter(
            Q(interface_templates__config_templates__device_type__isnull=True)
            | Q(interface_templates__config_templates__device_type=device.device_type)
        )
        .distinct()
        .order_by("name")
    )

    if not profiles.exists():
        # Fallback to all profiles (or device-role filtered if device has role)
        if device.role:
            return (
                models.InterfaceProfile.objects.filter(Q(device_roles__isnull=True) | Q(device_roles=device.role))
                .distinct()
                .order_by("name")
            )
        else:
            return models.InterfaceProfile.objects.filter(device_roles__isnull=True).order_by("name")

    # Apply device role filtering on the config-template-filtered queryset
    if device.role:
        profiles = profiles.filter(Q(device_roles__isnull=True) | Q(device_roles=device.role)).distinct()
    else:
        profiles = profiles.filter(device_roles__isnull=True)

    return profiles.order_by("name")


class InterfaceProfileAssignmentMenuHTMXView(View):
    """Render HTMX dropdown menu items for a single interface row."""

    def get(self, request, interface_id: int):
        if not request.user.has_perm("netbox_interface_profiles.view_interfaceprofileassignment"):
            return HttpResponseForbidden()

        interface = get_object_or_404(
            Interface.objects.restrict(request.user, "view").select_related(
                "device__platform",
                "device__device_type",
                "profile_assignment__interface_profile",
            ),
            pk=interface_id,
        )

        profiles = _get_applicable_profiles(interface.device)
        assignment = getattr(interface, "profile_assignment", None)
        current_profile = getattr(assignment, "interface_profile", None)

        if current_profile and not profiles.filter(pk=current_profile.pk).exists():
            profiles = (
                (profiles | models.InterfaceProfile.objects.filter(pk=current_profile.pk)).distinct().order_by("name")
            )

        # Profiles outside the user's permissions are listed but disabled, so it is clear they exist
        assignable_profile_ids = set(
            restrict_assignable_profiles(profiles, request.user, interface).values_list("pk", flat=True)
        )
        can_clear = (
            assignment is not None
            and models.InterfaceProfileAssignment.objects.restrict(request.user, "delete")
            .filter(pk=assignment.pk)
            .exists()
        )

        return render(
            request,
            "netbox_interface_profiles/inc/interface_profile_menu_items.html",
            {
                "interface": interface,
                "profiles": profiles,
                "current_profile": current_profile,
                "assignable_profile_ids": assignable_profile_ids,
                "can_clear": can_clear,
            },
        )


class InterfaceProfileAssignmentSetHTMXView(View):
    """Assign a profile to an interface via HTMX."""

    def post(self, request, interface_id: int, profile_id: int):
        can_add = request.user.has_perm("netbox_interface_profiles.add_interfaceprofileassignment")
        can_change = request.user.has_perm("netbox_interface_profiles.change_interfaceprofileassignment")
        if not (can_add or can_change):
            return HttpResponseForbidden()

        interface = get_object_or_404(Interface.objects.restrict(request.user, "view"), pk=interface_id)
        profile = get_object_or_404(models.InterfaceProfile.objects.all(), pk=profile_id)

        try:
            assign_profile(request.user, interface, profile)
        except PermissionsViolation:
            # A plain 403 is swallowed by HTMX; refresh so the message is shown instead
            messages.error(
                request,
                _("You are not permitted to assign {profile} to {interface}.").format(
                    profile=profile, interface=interface
                ),
            )
        except AbortRequest as exc:
            messages.error(request, exc.message)
        return HttpResponse(status=204, headers={"HX-Refresh": "true"})


class InterfaceProfileAssignmentRemoveHTMXView(View):
    """Remove a profile assignment from an interface via HTMX."""

    def post(self, request, interface_id: int):
        if not request.user.has_perm("netbox_interface_profiles.delete_interfaceprofileassignment"):
            return HttpResponseForbidden()

        assignment = (
            models.InterfaceProfileAssignment.objects.select_related("interface", "interface_profile")
            .filter(interface_id=interface_id)
            .first()
        )
        if assignment is None:
            return HttpResponse(status=204, headers={"HX-Refresh": "true"})

        if models.InterfaceProfileAssignment.objects.restrict(request.user, "delete").filter(pk=assignment.pk).exists():
            assignment.delete()
        else:
            messages.error(
                request,
                _("You are not permitted to remove {profile} from {interface}.").format(
                    profile=assignment.interface_profile, interface=assignment.interface
                ),
            )
        return HttpResponse(status=204, headers={"HX-Refresh": "true"})
