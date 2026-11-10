"""
Test cases for recording and showing interface role synchronizations.
"""

import uuid

from core.choices import JobStatusChoices
from core.models import Job
from dcim.choices import InterfaceModeChoices, InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from ipam.models import VLAN, VLANGroup
from users.models import ObjectPermission
from utilities.exceptions import AbortRequest
from utilities.permissions import resolve_permission_type

from ..jobs import SyncInterfaceRoleJob
from ..models import InterfaceRole, InterfaceRoleAssignment, InterfaceTemplate, RoleSync, RoleSyncChange
from ..services import describe_changes, run_role_sync
from ..testing import PluginViewTestCase


class RoleSyncTestMixin:
    """Create a role assigned to two interfaces, of which only one deviates from the role's template."""

    @classmethod
    def setUpTestData(cls):
        cls.role = InterfaceRole.objects.create(name="Sync Role")
        site = Site.objects.create(name="Site-Sync", slug="site-sync")
        manufacturer = Manufacturer.objects.create(name="Manufacturer-Sync", slug="manufacturer-sync")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Type-Sync", slug="type-sync")
        role = DeviceRole.objects.create(name="Role-Sync", slug="role-sync")
        cls.device = Device.objects.create(name="Device-Sync", site=site, device_type=device_type, role=role)

        vlan_group = VLANGroup.objects.create(
            name="VG-Sync",
            slug="vg-sync",
            scope_type=ContentType.objects.get_for_model(Site),
            scope_id=site.pk,
        )
        cls.untagged_vlan = VLAN.objects.create(name="Users", vid=10, site=site, group=vlan_group)
        cls.tagged_vlan = VLAN.objects.create(name="Voice", vid=20, site=site, group=vlan_group)

        cls.interface = Interface.objects.create(
            device=cls.device, name="eth0", type=InterfaceTypeChoices.TYPE_1GE_FIXED, enabled=False
        )
        cls.in_sync_interface = Interface.objects.create(
            device=cls.device,
            name="eth1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            enabled=True,
            mtu=9000,
            mode=InterfaceModeChoices.MODE_TAGGED,
            untagged_vlan=cls.untagged_vlan,
        )
        cls.in_sync_interface.tagged_vlans.set([cls.tagged_vlan])

        # Assign before adding the template, so the assignment signal leaves the interfaces untouched
        for interface in (cls.interface, cls.in_sync_interface):
            InterfaceRoleAssignment.objects.create(interface=interface, interface_role=cls.role)
        InterfaceTemplate.objects.create(
            interface_role=cls.role,
            name="Global",
            enabled=True,
            mtu=9000,
            mode=InterfaceModeChoices.MODE_TAGGED,
            untagged_vlan_vid=10,
            tagged_vlans_vids=[20],
        )

    def create_sync(self, dry_run: bool, **job_attrs) -> RoleSync:
        job = Job.objects.create(name=SyncInterfaceRoleJob.name, job_id=uuid.uuid4(), **job_attrs)
        return RoleSync.objects.create(interface_role=self.role, job=job, dry_run=dry_run)


class RunRoleSyncTestCase(RoleSyncTestMixin, PluginViewTestCase):
    def test_dry_run_records_changes_without_saving_them(self):
        sync = self.create_sync(dry_run=True)

        changes = run_role_sync(sync)

        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].interface, self.interface)
        self.assertEqual(changes[0].device_name, "Device-Sync")
        self.assertEqual(
            set(changes[0].diff()),
            {"enabled", "mtu", "mode", "untagged_vlan", "tagged_vlans"},
        )
        self.assertEqual(changes[0].diff()["tagged_vlans"], ([], [self.tagged_vlan.pk]))
        self.assertEqual(sync.interface_count, 2)

        self.interface.refresh_from_db()
        self.assertFalse(self.interface.enabled)
        self.assertIsNone(self.interface.mtu)
        self.assertFalse(self.interface.tagged_vlans.exists())

    def test_commit_saves_and_records_changes(self):
        sync = self.create_sync(dry_run=False)

        changes = run_role_sync(sync)

        self.assertEqual(len(changes), 1)
        self.interface.refresh_from_db()
        self.assertTrue(self.interface.enabled)
        self.assertEqual(self.interface.mtu, 9000)
        self.assertEqual(list(self.interface.tagged_vlans.all()), [self.tagged_vlan])

        # A second run finds nothing left to change
        self.assertEqual(run_role_sync(self.create_sync(dry_run=False)), [])

    def test_describe_changes_resolves_labels_and_objects(self):
        sync = self.create_sync(dry_run=True)
        run_role_sync(sync)

        rows = describe_changes(RoleSyncChange.objects.filter(sync=sync))

        self.assertEqual(len(rows), 1)
        values = {str(attribute["label"]): (attribute["old"], attribute["new"]) for attribute in rows[0]["attributes"]}
        self.assertEqual(values["enabled"], (False, True))
        self.assertEqual(values["untagged VLAN"], (None, self.untagged_vlan))
        self.assertEqual(values["tagged VLANs"], ([], [self.tagged_vlan]))
        self.assertEqual(values["mode"], (None, "Tagged"))

    def test_job_runs_linked_sync(self):
        sync = self.create_sync(dry_run=True)

        SyncInterfaceRoleJob.handle(sync.job)

        self.assertEqual(Job.objects.get(interface_role_sync=sync).status, JobStatusChoices.STATUS_COMPLETED)
        self.assertEqual(RoleSyncChange.objects.filter(sync=sync).count(), 1)


class RoleSyncPermissionTestCase(RoleSyncTestMixin, PluginViewTestCase):
    """A synchronization may only change interfaces its user is permitted to change."""

    def add_interface_change_permission(self, constraints):
        object_type, _ = resolve_permission_type("dcim.change_interface")
        permission = ObjectPermission.objects.create(
            name="Change interfaces", actions=["change"], constraints=constraints
        )
        permission.users.add(self.user)
        permission.object_types.add(object_type)

    def assertInterfaceUnchanged(self):
        self.interface.refresh_from_db()
        self.assertFalse(self.interface.enabled)
        self.assertIsNone(self.interface.mtu)

    def test_sync_within_constraints_changes_interfaces(self):
        self.add_interface_change_permission({"device__name": "Device-Sync"})

        changes = run_role_sync(self.create_sync(dry_run=False, user=self.user))

        self.assertEqual(len(changes), 1)
        self.interface.refresh_from_db()
        self.assertTrue(self.interface.enabled)

    def test_sync_of_interface_outside_constraints_is_rejected(self):
        self.add_interface_change_permission({"device__name": "Other Device"})

        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run):
                sync = self.create_sync(dry_run=dry_run, user=self.user)
                with self.assertRaisesMessage(AbortRequest, "not permitted to change Device-Sync eth0"):
                    run_role_sync(sync)

                self.assertInterfaceUnchanged()
                self.assertFalse(RoleSyncChange.objects.filter(sync=sync).exists())

    def test_sync_resulting_in_interface_outside_constraints_is_rejected(self):
        """Constraints also apply to the interface after synchronization, as in NetBox's edit views."""
        self.add_interface_change_permission({"enabled": False})

        with self.assertRaises(AbortRequest):
            run_role_sync(self.create_sync(dry_run=False, user=self.user))

        self.assertInterfaceUnchanged()

    def test_job_fails_when_sync_is_not_permitted(self):
        sync = self.create_sync(dry_run=False, user=self.user)

        SyncInterfaceRoleJob.handle(sync.job)

        job = Job.objects.get(interface_role_sync=sync)
        self.assertEqual(job.status, JobStatusChoices.STATUS_FAILED)
        self.assertIn("not permitted", job.error)
        self.assertInterfaceUnchanged()


class RoleSyncViewTestCase(RoleSyncTestMixin, PluginViewTestCase):
    def test_sync_view_creates_sync_and_redirects_to_it(self):
        self.add_permissions(
            "dcim.change_interface",
            "interface_profiles.view_interfacerole",
            "interface_profiles.view_rolesync",
        )

        url = reverse("plugins:interface_profiles:interfacerole_sync", kwargs={"pk": self.role.pk})
        response = self.client.post(url, {"dry_run": "on"})

        sync = RoleSync.objects.get(interface_role=self.role)
        self.assertTrue(sync.dry_run)
        self.assertEqual(sync.job.object, self.role)
        self.assertRedirects(response, sync.get_absolute_url(), fetch_redirect_response=False)

    def test_sync_detail_shows_proposed_changes(self):
        self.add_permissions("dcim.change_interface", "interface_profiles.view_rolesync")
        sync = self.create_sync(dry_run=True, status=JobStatusChoices.STATUS_COMPLETED)
        run_role_sync(sync)

        response = self.client.get(sync.get_absolute_url())

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Proposed Changes")
        self.assertContains(response, "Apply Changes")
        self.assertContains(response, "eth0")
        self.assertContains(response, "Voice (20)")
        self.assertNotContains(response, "eth1")
        self.assertNotContains(response, "hx-trigger")

    def test_sync_detail_polls_while_running(self):
        self.add_permissions("interface_profiles.view_rolesync")
        sync = self.create_sync(dry_run=True, status=JobStatusChoices.STATUS_RUNNING)

        response = self.client.get(sync.get_absolute_url())

        self.assertHttpStatus(response, 200)
        self.assertContains(response, 'hx-trigger="every 2s"')
        self.assertNotContains(response, "Apply Changes")

    def test_core_job_page_renders_for_sync_job(self):
        """The core job page links to the role's Jobs tab, which must resolve."""
        self.add_permissions("core.view_job", "interface_profiles.view_interfacerole")
        sync = self.create_sync(dry_run=True, status=JobStatusChoices.STATUS_COMPLETED)
        job = Job.objects.get(interface_role_sync=sync)
        job.object = self.role
        job.save()

        response = self.client.get(reverse("core:job", kwargs={"pk": job.pk}))
        self.assertHttpStatus(response, 200)

        response = self.client.get(
            reverse("plugins:interface_profiles:interfacerole_jobs", kwargs={"pk": self.role.pk})
        )
        self.assertHttpStatus(response, 200)

    def test_sync_list_and_role_tab(self):
        self.add_permissions(
            "interface_profiles.view_rolesync",
            "interface_profiles.view_interfacerole",
        )
        sync = self.create_sync(dry_run=False, status=JobStatusChoices.STATUS_COMPLETED)
        run_role_sync(sync)

        for url in (
            reverse("plugins:interface_profiles:rolesync_list"),
            reverse("plugins:interface_profiles:interfacerole_syncs", kwargs={"pk": self.role.pk}),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertHttpStatus(response, 200)
                self.assertContains(response, sync.get_absolute_url())

    def test_sync_list_offers_bulk_actions(self):
        self.add_permissions("interface_profiles.view_rolesync", "interface_profiles.delete_rolesync")
        sync = self.create_sync(dry_run=True, status=JobStatusChoices.STATUS_COMPLETED)

        response = self.client.get(reverse("plugins:interface_profiles:rolesync_list"))

        self.assertHttpStatus(response, 200)
        self.assertContains(response, f'name="pk" value="{sync.pk}"')
        self.assertContains(response, reverse("plugins:interface_profiles:rolesync_bulk_delete"))

    def test_bulk_delete_syncs(self):
        self.add_permissions("interface_profiles.view_rolesync", "interface_profiles.delete_rolesync")
        syncs = [self.create_sync(dry_run=True, status=JobStatusChoices.STATUS_COMPLETED) for _ in range(2)]
        run_role_sync(syncs[0])

        response = self.client.post(
            reverse("plugins:interface_profiles:rolesync_bulk_delete"),
            {"pk": [sync.pk for sync in syncs], "confirm": True, "_confirm": True},
        )

        self.assertHttpStatus(response, 302)
        self.assertFalse(RoleSync.objects.exists())
        self.assertFalse(RoleSyncChange.objects.exists())

    def test_delete_sync(self):
        self.add_permissions("interface_profiles.view_rolesync", "interface_profiles.delete_rolesync")
        sync = self.create_sync(dry_run=True, status=JobStatusChoices.STATUS_COMPLETED)

        url = reverse("plugins:interface_profiles:rolesync_delete", kwargs={"pk": sync.pk})
        self.assertContains(self.client.get(sync.get_absolute_url()), url)
        response = self.client.post(url, {"confirm": True})

        self.assertHttpStatus(response, 302)
        self.assertFalse(RoleSync.objects.filter(pk=sync.pk).exists())

    def test_export_syncs(self):
        self.add_permissions("interface_profiles.view_rolesync")
        self.create_sync(dry_run=True, status=JobStatusChoices.STATUS_COMPLETED)

        response = self.client.get(reverse("plugins:interface_profiles:rolesync_list"), {"export": "table"})

        self.assertHttpStatus(response, 200)
        self.assertIn("Dry run", response.content.decode())
