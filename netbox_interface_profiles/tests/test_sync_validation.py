"""
Test cases for reporting interfaces that a role would make invalid.
"""

import uuid

from core.choices import JobStatusChoices
from core.models import Job
from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from django.contrib.messages import get_messages
from django.urls import reverse
from extras.models import Notification
from ipam.models import VLAN

from ..jobs import SyncInterfaceRoleJob
from ..models import InterfaceRole, InterfaceRoleAssignment, InterfaceTemplate, RoleSync
from ..testing import PluginAPITestCase, PluginModelTestCase, PluginViewTestCase
from ..testing.utils import disable_warnings

EXPECTED_ERROR = (
    "Role Invalid Role cannot be applied to Device-Invalid eth0: "
    "untagged VLAN: Interface mode does not support an untagged vlan."
)


class InvalidRoleMixin(PluginModelTestCase):
    """A role setting an untagged VLAN without a mode, which NetBox rejects on an interface without a mode."""

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name="Site-Invalid", slug="site-invalid")
        manufacturer = Manufacturer.objects.create(name="Manufacturer-Invalid", slug="manufacturer-invalid")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Type-Invalid", slug="type-invalid")
        role = DeviceRole.objects.create(name="Role-Invalid", slug="role-invalid")
        cls.device = Device.objects.create(name="Device-Invalid", site=site, device_type=device_type, role=role)
        cls.interface = Interface.objects.create(
            device=cls.device, name="eth0", type=InterfaceTypeChoices.TYPE_1GE_FIXED, enabled=False
        )
        VLAN.objects.create(name="Users", vid=10, site=site)

        cls.role = InterfaceRole.objects.create(name="Invalid Role")
        InterfaceTemplate.objects.create(interface_role=cls.role, name="Global", enabled=True, untagged_vlan_vid=10)

    def assertNothingChanged(self):
        self.assertFalse(InterfaceRoleAssignment.objects.filter(interface=self.interface).exists())
        self.interface.refresh_from_db()
        self.assertFalse(self.interface.enabled)
        self.assertIsNone(self.interface.untagged_vlan)


class AssignmentValidationViewTestCase(InvalidRoleMixin, PluginViewTestCase):
    def setUp(self):
        super().setUp()
        self.add_permissions(
            "dcim.view_device",
            "dcim.view_interface",
            "netbox_interface_profiles.view_interfacerole",
            "netbox_interface_profiles.view_interfaceroleassignment",
            "netbox_interface_profiles.add_interfaceroleassignment",
            "netbox_interface_profiles.change_interfaceroleassignment",
        )

    def test_edit_form_shows_error(self):
        response = self.client.post(
            reverse("plugins:netbox_interface_profiles:interfaceroleassignment_add"),
            {"interface": self.interface.pk, "interface_role": self.role.pk},
        )

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "cannot be applied to Device-Invalid eth0")
        self.assertNothingChanged()

    def test_interface_menu_shows_error(self):
        response = self.client.post(
            reverse(
                "plugins:netbox_interface_profiles:interfaceroleassignment_htmx_set",
                kwargs={"interface_id": self.interface.pk, "role_id": self.role.pk},
            )
        )

        self.assertHttpStatus(response, 204)
        self.assertEqual([str(m) for m in get_messages(response.wsgi_request)], [EXPECTED_ERROR])
        self.assertNothingChanged()

    def test_device_tab_shows_error(self):
        response = self.client.post(
            reverse("dcim:device_interface_roles", kwargs={"pk": self.device.pk}),
            {"pk": [self.interface.pk], "_assign": self.role.pk},
        )

        self.assertHttpStatus(response, 302)
        self.assertEqual(
            [str(m) for m in get_messages(response.wsgi_request)], [f"{EXPECTED_ERROR} No changes were made."]
        )
        self.assertNothingChanged()


class AssignmentValidationAPITestCase(InvalidRoleMixin, PluginAPITestCase):
    def test_api_returns_error(self):
        self.add_permissions(
            "dcim.view_interface",
            "netbox_interface_profiles.view_interfacerole",
            "netbox_interface_profiles.add_interfaceroleassignment",
        )

        with disable_warnings("django.request"):
            response = self.client.post(
                reverse("plugins-api:netbox_interface_profiles-api:interfaceroleassignment-list"),
                {"interface": self.interface.pk, "interface_role": self.role.pk},
                format="json",
            )

        self.assertHttpStatus(response, 400)
        self.assertEqual(response.json()["detail"], EXPECTED_ERROR)
        self.assertNothingChanged()


class SyncJobValidationTestCase(InvalidRoleMixin, PluginViewTestCase):
    def test_failed_sync_notifies_user_and_shows_error(self):
        self.add_permissions("netbox_interface_profiles.view_rolesync")

        # Assign while the role has no template yet, so the assignment itself goes through
        template = InterfaceTemplate.objects.get(interface_role=self.role)
        template.interface_role = InterfaceRole.objects.create(name="Other Role")
        template.save()
        InterfaceRoleAssignment.objects.create(interface=self.interface, interface_role=self.role)
        template.interface_role = self.role
        template.save()

        job = Job.objects.create(name=SyncInterfaceRoleJob.name, job_id=uuid.uuid4(), user=self.user)
        sync = RoleSync.objects.create(interface_role=self.role, job=job, dry_run=False)

        SyncInterfaceRoleJob.handle(job)

        job.refresh_from_db()
        self.assertEqual(job.status, JobStatusChoices.STATUS_FAILED)
        self.assertEqual(job.error, EXPECTED_ERROR)
        self.assertTrue(Notification.objects.filter(user=self.user, object_id=job.pk).exists())

        response = self.client.get(sync.get_absolute_url())
        self.assertContains(response, "Synchronization failed")
        self.assertContains(response, "cannot be applied to Device-Invalid eth0")
        self.assertContains(response, "All changes were rolled back.")

        self.interface.refresh_from_db()
        self.assertIsNone(self.interface.untagged_vlan)
