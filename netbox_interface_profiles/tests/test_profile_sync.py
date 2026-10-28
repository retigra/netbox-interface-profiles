"""
Test cases for recording and showing interface profile synchronizations.
"""

import uuid

from core.choices import JobStatusChoices
from core.models import Job
from dcim.choices import InterfaceModeChoices, InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from ipam.models import VLAN, VLANGroup

from ..jobs import SyncInterfaceProfileJob
from ..models import InterfaceProfile, InterfaceProfileAssignment, InterfaceTemplate, ProfileSync, ProfileSyncChange
from ..services import describe_changes, run_profile_sync
from ..testing import PluginViewTestCase


class ProfileSyncTestMixin:
    """Create a profile assigned to two interfaces, of which only one deviates from the profile's template."""

    @classmethod
    def setUpTestData(cls):
        cls.profile = InterfaceProfile.objects.create(name="Sync Profile")
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
            InterfaceProfileAssignment.objects.create(interface=interface, interface_profile=cls.profile)
        InterfaceTemplate.objects.create(
            interface_profile=cls.profile,
            name="Global",
            enabled=True,
            mtu=9000,
            mode=InterfaceModeChoices.MODE_TAGGED,
            untagged_vlan_vid=10,
            tagged_vlans_vids=[20],
        )

    def create_sync(self, dry_run: bool, **job_attrs) -> ProfileSync:
        job = Job.objects.create(name=SyncInterfaceProfileJob.name, job_id=uuid.uuid4(), **job_attrs)
        return ProfileSync.objects.create(interface_profile=self.profile, job=job, dry_run=dry_run)


class RunProfileSyncTestCase(ProfileSyncTestMixin, PluginViewTestCase):
    def test_dry_run_records_changes_without_saving_them(self):
        sync = self.create_sync(dry_run=True)

        changes = run_profile_sync(sync)

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

        changes = run_profile_sync(sync)

        self.assertEqual(len(changes), 1)
        self.interface.refresh_from_db()
        self.assertTrue(self.interface.enabled)
        self.assertEqual(self.interface.mtu, 9000)
        self.assertEqual(list(self.interface.tagged_vlans.all()), [self.tagged_vlan])

        # A second run finds nothing left to change
        self.assertEqual(run_profile_sync(self.create_sync(dry_run=False)), [])

    def test_describe_changes_resolves_labels_and_objects(self):
        sync = self.create_sync(dry_run=True)
        run_profile_sync(sync)

        rows = describe_changes(ProfileSyncChange.objects.filter(sync=sync))

        self.assertEqual(len(rows), 1)
        values = {str(attribute["label"]): (attribute["old"], attribute["new"]) for attribute in rows[0]["attributes"]}
        self.assertEqual(values["enabled"], (False, True))
        self.assertEqual(values["untagged VLAN"], (None, self.untagged_vlan))
        self.assertEqual(values["tagged VLANs"], ([], [self.tagged_vlan]))
        self.assertEqual(values["mode"], (None, "Tagged"))

    def test_job_runs_linked_sync(self):
        sync = self.create_sync(dry_run=True)

        SyncInterfaceProfileJob.handle(sync.job)

        self.assertEqual(Job.objects.get(interface_profile_sync=sync).status, JobStatusChoices.STATUS_COMPLETED)
        self.assertEqual(ProfileSyncChange.objects.filter(sync=sync).count(), 1)


class ProfileSyncViewTestCase(ProfileSyncTestMixin, PluginViewTestCase):
    def test_sync_view_creates_sync_and_redirects_to_it(self):
        self.add_permissions("dcim.change_interface", "netbox_interface_profiles.view_profilesync")

        url = reverse("plugins:netbox_interface_profiles:interfaceprofile_sync", kwargs={"pk": self.profile.pk})
        response = self.client.post(url, {"dry_run": "on"})

        sync = ProfileSync.objects.get(interface_profile=self.profile)
        self.assertTrue(sync.dry_run)
        self.assertEqual(sync.job.object, self.profile)
        self.assertRedirects(response, sync.get_absolute_url(), fetch_redirect_response=False)

    def test_sync_detail_shows_proposed_changes(self):
        self.add_permissions("dcim.change_interface", "netbox_interface_profiles.view_profilesync")
        sync = self.create_sync(dry_run=True, status=JobStatusChoices.STATUS_COMPLETED)
        run_profile_sync(sync)

        response = self.client.get(sync.get_absolute_url())

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Proposed Changes")
        self.assertContains(response, "Apply Changes")
        self.assertContains(response, "eth0")
        self.assertContains(response, "Voice (20)")
        self.assertNotContains(response, "eth1")
        self.assertNotContains(response, "hx-trigger")

    def test_sync_detail_polls_while_running(self):
        self.add_permissions("netbox_interface_profiles.view_profilesync")
        sync = self.create_sync(dry_run=True, status=JobStatusChoices.STATUS_RUNNING)

        response = self.client.get(sync.get_absolute_url())

        self.assertHttpStatus(response, 200)
        self.assertContains(response, 'hx-trigger="every 2s"')
        self.assertNotContains(response, "Apply Changes")

    def test_core_job_page_renders_for_sync_job(self):
        """The core job page links to the profile's Jobs tab, which must resolve."""
        self.add_permissions("core.view_job", "netbox_interface_profiles.view_interfaceprofile")
        sync = self.create_sync(dry_run=True, status=JobStatusChoices.STATUS_COMPLETED)
        job = Job.objects.get(interface_profile_sync=sync)
        job.object = self.profile
        job.save()

        response = self.client.get(reverse("core:job", kwargs={"pk": job.pk}))
        self.assertHttpStatus(response, 200)

        response = self.client.get(
            reverse("plugins:netbox_interface_profiles:interfaceprofile_jobs", kwargs={"pk": self.profile.pk})
        )
        self.assertHttpStatus(response, 200)

    def test_sync_list_and_profile_tab(self):
        self.add_permissions(
            "netbox_interface_profiles.view_profilesync",
            "netbox_interface_profiles.view_interfaceprofile",
        )
        sync = self.create_sync(dry_run=False, status=JobStatusChoices.STATUS_COMPLETED)
        run_profile_sync(sync)

        for url in (
            reverse("plugins:netbox_interface_profiles:profilesync_list"),
            reverse("plugins:netbox_interface_profiles:interfaceprofile_syncs", kwargs={"pk": self.profile.pk}),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertHttpStatus(response, 200)
                self.assertContains(response, sync.get_absolute_url())

    def test_sync_list_offers_bulk_actions(self):
        self.add_permissions(
            "netbox_interface_profiles.view_profilesync", "netbox_interface_profiles.delete_profilesync"
        )
        sync = self.create_sync(dry_run=True, status=JobStatusChoices.STATUS_COMPLETED)

        response = self.client.get(reverse("plugins:netbox_interface_profiles:profilesync_list"))

        self.assertHttpStatus(response, 200)
        self.assertContains(response, f'name="pk" value="{sync.pk}"')
        self.assertContains(response, reverse("plugins:netbox_interface_profiles:profilesync_bulk_delete"))

    def test_bulk_delete_syncs(self):
        self.add_permissions(
            "netbox_interface_profiles.view_profilesync", "netbox_interface_profiles.delete_profilesync"
        )
        syncs = [self.create_sync(dry_run=True, status=JobStatusChoices.STATUS_COMPLETED) for _ in range(2)]
        run_profile_sync(syncs[0])

        response = self.client.post(
            reverse("plugins:netbox_interface_profiles:profilesync_bulk_delete"),
            {"pk": [sync.pk for sync in syncs], "confirm": True, "_confirm": True},
        )

        self.assertHttpStatus(response, 302)
        self.assertFalse(ProfileSync.objects.exists())
        self.assertFalse(ProfileSyncChange.objects.exists())

    def test_delete_sync(self):
        self.add_permissions(
            "netbox_interface_profiles.view_profilesync", "netbox_interface_profiles.delete_profilesync"
        )
        sync = self.create_sync(dry_run=True, status=JobStatusChoices.STATUS_COMPLETED)

        url = reverse("plugins:netbox_interface_profiles:profilesync_delete", kwargs={"pk": sync.pk})
        self.assertContains(self.client.get(sync.get_absolute_url()), url)
        response = self.client.post(url, {"confirm": True})

        self.assertHttpStatus(response, 302)
        self.assertFalse(ProfileSync.objects.filter(pk=sync.pk).exists())

    def test_export_syncs(self):
        self.add_permissions("netbox_interface_profiles.view_profilesync")
        self.create_sync(dry_run=True, status=JobStatusChoices.STATUS_COMPLETED)

        response = self.client.get(reverse("plugins:netbox_interface_profiles:profilesync_list"), {"export": "table"})

        self.assertHttpStatus(response, 200)
        self.assertIn("Dry run", response.content.decode())
