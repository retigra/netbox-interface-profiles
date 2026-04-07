"""
InterfaceProfileAssignment views for netbox interface profiles.
"""

from dcim.filtersets import InterfaceFilterSet
from dcim.forms import InterfaceFilterForm
from dcim.models import Device, Interface
from dcim.views import DeviceComponentsView
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from netbox.object_actions import ObjectAction
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from .. import filtersets, forms, models, tables


class DeviceInterfaceTabSelectAction(ObjectAction):
    """Enable row selection on the device interface profiles tab."""

    name = "bulk_edit"
    label = "Select"
    multi = True
    permissions_required = set()
    template_name = "buttons/bulk_edit.html"


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


@register_model_view(Device, name="interface_profiles", path="interface-profiles")
class DeviceInterfaceProfileTabView(DeviceComponentsView):
    """Tab on the Device detail page showing all interfaces with their assigned profile."""

    queryset = Device.objects.all()
    child_model = Interface
    table = tables.DeviceInterfaceTable
    filterset = InterfaceFilterSet
    filterset_form = InterfaceFilterForm
    actions = (DeviceInterfaceTabSelectAction,)
    template_name = "netbox_interface_profiles/device_interface_profiles_tab.html"
    tab = ViewTab(
        label="Interface Profiles",
        badge=lambda obj: Interface.objects.filter(device=obj).count(),
        permission="netbox_interface_profiles.view_interfaceprofileassignment",
    )

    def get_children(self, request, parent):
        return (
            Interface.objects.restrict(request.user, "view")
            .filter(device=parent)
            .select_related("profile_assignment__interface_profile")
            .order_by("name")
        )

    def get_extra_context(self, request, instance):
        return {
            "bulk_assign_form": forms.DeviceBulkAssignProfileForm(device=instance),
        }

    def post(self, request, **kwargs):
        device = get_object_or_404(self.queryset, **kwargs)
        selected_pks = request.POST.getlist("pk")

        if not selected_pks:
            messages.warning(request, _("No interfaces selected."))
            return redirect(request.path)

        interfaces = Interface.objects.filter(device=device, pk__in=selected_pks)

        if "_assign" in request.POST:
            assign_form = forms.DeviceBulkAssignProfileForm(request.POST)
            if assign_form.is_valid():
                profile = assign_form.cleaned_data["interface_profile"]

                if not profile:
                    messages.error(request, _("Please select a valid Interface Profile."))
                    return redirect(request.path)

                created = updated = 0
                for iface in interfaces:
                    _assignment, was_created = models.InterfaceProfileAssignment.objects.update_or_create(
                        interface=iface,
                        defaults={"interface_profile": profile},
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                if created:
                    messages.success(request, _(f"Assigned profile to {created} interface(s)."))
                if updated:
                    messages.success(request, _(f"Updated profile for {updated} interface(s)."))
            else:
                messages.error(request, _("Please select a valid Interface Profile."))

        elif "_remove" in request.POST:
            assignments = list(
                models.InterfaceProfileAssignment.objects.select_related("interface", "interface_profile").filter(
                    interface__in=interfaces
                )
            )
            deleted = 0
            for assignment in assignments:
                assignment.delete()
                deleted += 1
            messages.success(request, _(f"Removed {deleted} profile assignment(s)."))

        return redirect(request.path)


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
            config_templates__platform=device.platform,
        )
        .filter(Q(config_templates__device_type__isnull=True) | Q(config_templates__device_type=device.device_type))
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
            Interface.objects.select_related(
                "device__platform",
                "device__device_type",
                "profile_assignment__interface_profile",
            ),
            pk=interface_id,
        )

        profiles = _get_applicable_profiles(interface.device)
        current_profile = getattr(getattr(interface, "profile_assignment", None), "interface_profile", None)

        if current_profile and not profiles.filter(pk=current_profile.pk).exists():
            profiles = (
                (profiles | models.InterfaceProfile.objects.filter(pk=current_profile.pk)).distinct().order_by("name")
            )

        return render(
            request,
            "netbox_interface_profiles/inc/interface_profile_menu_items.html",
            {
                "interface": interface,
                "profiles": profiles,
                "current_profile": current_profile,
            },
        )


class InterfaceProfileAssignmentSetHTMXView(View):
    """Assign a profile to an interface via HTMX."""

    def post(self, request, interface_id: int, profile_id: int):
        can_add = request.user.has_perm("netbox_interface_profiles.add_interfaceprofileassignment")
        can_change = request.user.has_perm("netbox_interface_profiles.change_interfaceprofileassignment")
        if not (can_add or can_change):
            return HttpResponseForbidden()

        interface = get_object_or_404(Interface.objects.all(), pk=interface_id)
        profile = get_object_or_404(models.InterfaceProfile.objects.all(), pk=profile_id)

        models.InterfaceProfileAssignment.objects.update_or_create(
            interface=interface,
            defaults={"interface_profile": profile},
        )
        return HttpResponse(status=204, headers={"HX-Refresh": "true"})


class InterfaceProfileAssignmentRemoveHTMXView(View):
    """Remove a profile assignment from an interface via HTMX."""

    def post(self, request, interface_id: int):
        if not request.user.has_perm("netbox_interface_profiles.delete_interfaceprofileassignment"):
            return HttpResponseForbidden()

        assignments = list(
            models.InterfaceProfileAssignment.objects.select_related("interface", "interface_profile").filter(
                interface_id=interface_id
            )
        )
        for assignment in assignments:
            assignment.delete()
        return HttpResponse(status=204, headers={"HX-Refresh": "true"})
