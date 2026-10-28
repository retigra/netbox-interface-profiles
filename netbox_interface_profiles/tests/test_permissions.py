"""
Test cases for role group based assignment permissions.
"""

from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from django.contrib.messages import get_messages
from django.urls import reverse
from users.models import ObjectPermission, User
from utilities.permissions import resolve_permission_type

from ..models import InterfaceRole, InterfaceRoleAssignment, RoleGroup
from ..permissions import restrict_assignable_roles
from ..testing import PluginAPITestCase, PluginViewTestCase
from ..testing.utils import disable_warnings

ACCESS_ONLY = {"interface_role__group__slug": "access"}


class RoleGroupPermissionMixin:
    """Shared fixtures: an access and a trunk role, an unassigned and a trunk-assigned interface."""

    user: User

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name="Permission Site", slug="permission-site")
        manufacturer = Manufacturer.objects.create(name="Permission Manufacturer", slug="permission-manufacturer")
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="Permission Type", slug="permission-type"
        )
        role = DeviceRole.objects.create(name="Permission Role", slug="permission-role")
        cls.device = Device.objects.create(name="Switch 1", site=cls.site, device_type=device_type, role=role)
        cls.free_interface = Interface.objects.create(
            device=cls.device, name="Gi0/1", type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        cls.trunk_interface = Interface.objects.create(
            device=cls.device, name="Gi0/48", type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )

        access_group = RoleGroup.objects.create(name="Access", slug="access")
        trunk_group = RoleGroup.objects.create(name="Trunk", slug="trunk")
        cls.access_role = InterfaceRole.objects.create(name="Access VLAN 10", group=access_group)
        cls.trunk_role = InterfaceRole.objects.create(name="Uplink Trunk", group=trunk_group)
        InterfaceRoleAssignment.objects.create(interface=cls.trunk_interface, interface_role=cls.trunk_role)

    def add_constrained_permission(self, actions: list[str], constraints):
        """Grant assignment actions to the test user, limited by the given constraints."""
        object_type, _ = resolve_permission_type("netbox_interface_profiles.view_interfaceroleassignment")
        permission = ObjectPermission.objects.create(
            name=f"Assignments {'/'.join(actions)}", actions=actions, constraints=constraints
        )
        permission.users.add(self.user)
        permission.object_types.add(object_type)

    def assigned_role(self, interface):
        assignment = InterfaceRoleAssignment.objects.filter(interface=interface).first()
        return assignment.interface_role if assignment else None


class RestrictAssignableRolesTestCase(RoleGroupPermissionMixin, PluginViewTestCase):
    """Test translating assignment constraints into assignable roles."""

    def assignable(self, interface=None):
        return set(restrict_assignable_roles(InterfaceRole.objects.all(), self.user, interface))

    def test_unconstrained_permission_allows_all_roles(self):
        self.add_permissions(
            "netbox_interface_profiles.add_interfaceroleassignment",
            "netbox_interface_profiles.change_interfaceroleassignment",
        )

        self.assertEqual(self.assignable(), {self.access_role, self.trunk_role})

    def test_group_constraint_limits_roles(self):
        self.add_constrained_permission(["add", "change"], ACCESS_ONLY)

        self.assertEqual(self.assignable(), {self.access_role})
        self.assertEqual(self.assignable(self.free_interface), {self.access_role})

    def test_constraint_sets_are_combined(self):
        self.add_constrained_permission(["add"], [ACCESS_ONLY, {"interface_role__name": "Uplink Trunk"}])

        self.assertEqual(self.assignable(self.free_interface), {self.access_role, self.trunk_role})

    def test_direct_role_constraint(self):
        self.add_constrained_permission(["add"], {"interface_role__in": [self.trunk_role.pk]})

        self.assertEqual(self.assignable(self.free_interface), {self.trunk_role})

    def test_interface_constraint_is_evaluated_against_interface(self):
        self.add_constrained_permission(["add"], {**ACCESS_ONLY, "interface__device__site__slug": "other-site"})
        self.assertEqual(self.assignable(self.free_interface), set())

        self.add_constrained_permission(["add"], {**ACCESS_ONLY, "interface__device__site": self.site.pk})
        self.user = type(self.user).objects.get(pk=self.user.pk)  # Reset the permission cache
        self.assertEqual(self.assignable(self.free_interface), {self.access_role})

    def test_existing_assignment_outside_permission_offers_nothing(self):
        self.add_constrained_permission(["add", "change"], ACCESS_ONLY)

        self.assertEqual(self.assignable(self.trunk_interface), set())

    def test_missing_permission_offers_nothing(self):
        self.add_permissions("netbox_interface_profiles.add_interfaceroleassignment")

        # Bulk assignment needs both add and change
        self.assertEqual(self.assignable(), set())


class HTMXAssignmentPermissionTestCase(RoleGroupPermissionMixin, PluginViewTestCase):
    """Test that the per-interface HTMX actions enforce role group constraints."""

    def setUp(self):
        super().setUp()
        self.add_permissions("dcim.view_interface", "netbox_interface_profiles.view_interfaceroleassignment")

    def set_url(self, interface, role):
        return reverse(
            "plugins:netbox_interface_profiles:interfaceroleassignment_htmx_set",
            kwargs={"interface_id": interface.pk, "role_id": role.pk},
        )

    def test_assign_role_in_permitted_group(self):
        self.add_constrained_permission(["add", "change"], ACCESS_ONLY)

        response = self.client.post(self.set_url(self.free_interface, self.access_role))

        self.assertHttpStatus(response, 204)
        self.assertEqual(self.assigned_role(self.free_interface), self.access_role)

    def test_assign_role_outside_permitted_group_is_rejected(self):
        self.add_constrained_permission(["add", "change"], ACCESS_ONLY)

        response = self.client.post(self.set_url(self.free_interface, self.trunk_role))

        self.assertHttpStatus(response, 204)
        self.assertIsNone(self.assigned_role(self.free_interface))
        self.assertIn("not permitted", str(list(get_messages(response.wsgi_request))[0]))

    def test_change_of_assignment_outside_permitted_group_is_rejected(self):
        """Service desk may not repurpose a trunk port, not even to an access role."""
        self.add_constrained_permission(["add", "change"], ACCESS_ONLY)

        self.client.post(self.set_url(self.trunk_interface, self.access_role))

        self.assertEqual(self.assigned_role(self.trunk_interface), self.trunk_role)

    def test_remove_assignment_outside_permitted_group_is_rejected(self):
        self.add_constrained_permission(["delete"], ACCESS_ONLY)

        url = reverse(
            "plugins:netbox_interface_profiles:interfaceroleassignment_htmx_remove",
            kwargs={"interface_id": self.trunk_interface.pk},
        )
        response = self.client.post(url)

        self.assertHttpStatus(response, 204)
        self.assertEqual(self.assigned_role(self.trunk_interface), self.trunk_role)

    def test_menu_disables_roles_outside_permitted_group(self):
        self.add_constrained_permission(["add", "change", "delete"], ACCESS_ONLY)

        url = reverse(
            "plugins:netbox_interface_profiles:interfaceroleassignment_htmx_menu",
            kwargs={"interface_id": self.free_interface.pk},
        )
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertContains(response, self.trunk_role.name)
        self.assertEqual(response.context["assignable_role_ids"], {self.access_role.pk})
        self.assertFalse(response.context["can_clear"])

    def test_menu_hides_clear_for_assignment_outside_permitted_group(self):
        self.add_constrained_permission(["add", "change", "delete"], ACCESS_ONLY)

        url = reverse(
            "plugins:netbox_interface_profiles:interfaceroleassignment_htmx_menu",
            kwargs={"interface_id": self.trunk_interface.pk},
        )
        response = self.client.get(url)

        self.assertEqual(response.context["assignable_role_ids"], set())
        self.assertFalse(response.context["can_clear"])
        self.assertNotContains(response, "Clear Assignment")


class DeviceTabAssignmentPermissionTestCase(RoleGroupPermissionMixin, PluginViewTestCase):
    """Test that the device tab bulk actions enforce role group constraints."""

    def setUp(self):
        super().setUp()
        self.add_permissions(
            "dcim.view_device",
            "dcim.view_interface",
            "netbox_interface_profiles.view_interfacerole",
            "netbox_interface_profiles.view_interfaceroleassignment",
        )
        self.url = reverse("dcim:device_interface_roles", kwargs={"pk": self.device.pk})

    def test_bulk_assign_offers_only_permitted_roles(self):
        self.add_constrained_permission(["add", "change"], ACCESS_ONLY)

        response = self.client.get(self.url)

        self.assertContains(response, f'name="_assign" value="{self.access_role.pk}"')
        self.assertNotContains(response, f'name="_assign" value="{self.trunk_role.pk}"')

    def test_bulk_assign_outside_permitted_group_is_rejected(self):
        self.add_constrained_permission(["add", "change"], ACCESS_ONLY)

        response = self.client.post(self.url, {"pk": [self.free_interface.pk], "_assign": self.trunk_role.pk})

        self.assertHttpStatus(response, 302)
        self.assertIsNone(self.assigned_role(self.free_interface))

    def test_bulk_assign_is_rolled_back_when_any_interface_is_not_permitted(self):
        self.add_constrained_permission(["add", "change"], ACCESS_ONLY)

        self.client.post(
            self.url,
            {"pk": [self.free_interface.pk, self.trunk_interface.pk], "_assign": self.access_role.pk},
        )

        self.assertIsNone(self.assigned_role(self.free_interface))
        self.assertEqual(self.assigned_role(self.trunk_interface), self.trunk_role)

    def test_bulk_remove_skips_assignments_outside_permitted_group(self):
        self.add_constrained_permission(["delete"], ACCESS_ONLY)
        InterfaceRoleAssignment.objects.create(interface=self.free_interface, interface_role=self.access_role)

        response = self.client.post(self.url, {"pk": [self.free_interface.pk, self.trunk_interface.pk], "_remove": ""})

        self.assertHttpStatus(response, 302)
        self.assertIsNone(self.assigned_role(self.free_interface))
        self.assertEqual(self.assigned_role(self.trunk_interface), self.trunk_role)


class GenericAssignmentPermissionTestCase(RoleGroupPermissionMixin, PluginViewTestCase):
    """The standard NetBox edit view enforces the same constraints."""

    def test_add_view_rejects_role_outside_permitted_group(self):
        self.add_permissions("dcim.view_interface", "netbox_interface_profiles.view_interfacerole")
        self.add_constrained_permission(["add"], ACCESS_ONLY)

        url = reverse("plugins:netbox_interface_profiles:interfaceroleassignment_add")
        response = self.client.post(url, {"interface": self.free_interface.pk, "interface_role": self.trunk_role.pk})

        self.assertHttpStatus(response, 200)
        self.assertIsNone(self.assigned_role(self.free_interface))


class APIAssignmentPermissionTestCase(RoleGroupPermissionMixin, PluginAPITestCase):
    """The REST API enforces the same constraints."""

    def test_create_assignment_outside_permitted_group_is_rejected(self):
        self.add_permissions("dcim.view_interface", "netbox_interface_profiles.view_interfacerole")
        self.add_constrained_permission(["add"], ACCESS_ONLY)

        url = reverse("plugins-api:netbox_interface_profiles-api:interfaceroleassignment-list")
        with disable_warnings("django.request"):
            response = self.client.post(
                url,
                {"interface": self.free_interface.pk, "interface_role": self.trunk_role.pk},
                format="json",
            )

        self.assertHttpStatus(response, 403)
        self.assertIsNone(self.assigned_role(self.free_interface))

    def test_create_assignment_in_permitted_group(self):
        self.add_permissions("dcim.view_interface", "netbox_interface_profiles.view_interfacerole")
        self.add_constrained_permission(["add"], ACCESS_ONLY)

        url = reverse("plugins-api:netbox_interface_profiles-api:interfaceroleassignment-list")
        response = self.client.post(
            url,
            {"interface": self.free_interface.pk, "interface_role": self.access_role.pk},
            format="json",
        )

        self.assertHttpStatus(response, 201)
        self.assertEqual(self.assigned_role(self.free_interface), self.access_role)
