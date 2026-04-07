"""
Test cases for netbox interface profiles models.
"""

from dcim.choices import InterfaceModeChoices, InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site, SiteGroup
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from ipam.models import VLAN, VLANGroup

from ..models import InterfaceProfile, InterfaceTemplate
from ..testing import PluginModelTestCase
from ..testing.utils import create_tags, get_random_string


class InterfaceProfileTestCase(PluginModelTestCase):
    """Test InterfaceProfile model."""

    @classmethod
    def setUpTestData(cls):
        """Create three InterfaceProfile records."""
        InterfaceProfile.objects.create(
            name="Profile 1",
            description="First profile",
        )
        InterfaceProfile.objects.create(
            name="Profile 2",
            description="Second profile",
        )
        InterfaceProfile.objects.create(
            name="Profile 3",
            description="",
        )

    def test_create_interface_profile(self):
        """Test creating an InterfaceProfile instance."""
        name = f"Profile {get_random_string(10)}"
        instance = InterfaceProfile.objects.create(
            name=name,
            description="A test profile",
        )

        self.assertEqual(instance.name, name)
        self.assertEqual(instance.description, "A test profile")
        self.assertIsNotNone(instance.pk)

    def test_create_without_description(self):
        """Test that description is optional (blank allowed)."""
        instance = InterfaceProfile.objects.create(
            name=f"No Desc {get_random_string(6)}",
        )

        self.assertEqual(instance.description, "")

    def test_str_representation(self):
        """Test InterfaceProfile string representation returns name."""
        instance = InterfaceProfile.objects.first()
        self.assertEqual(str(instance), instance.name)

    def test_absolute_url_contains_pk(self):
        """Test get_absolute_url includes the instance PK."""
        instance = InterfaceProfile.objects.first()
        url = instance.get_absolute_url()

        self.assertIsNotNone(url)
        self.assertIn(str(instance.pk), url)

    def test_default_ordering(self):
        """Test that instances are ordered by name."""
        instances = list(InterfaceProfile.objects.all())
        names = [i.name for i in instances]
        self.assertEqual(names, sorted(names))

    def test_model_to_dict(self):
        """Test model_to_dict helper includes expected keys."""
        instance = InterfaceProfile.objects.first()
        data = self.model_to_dict(instance)

        self.assertIn("name", data)
        self.assertEqual(data["name"], instance.name)
        self.assertIn("id", data)

    def test_instance_equal(self):
        """Test assertInstanceEqual helper with matching data."""
        instance = InterfaceProfile.objects.first()
        self.assertInstanceEqual(
            instance,
            {"name": instance.name, "id": instance.pk},
        )

    def test_interface_profile_with_tags(self):
        """Test InterfaceProfile supports tags (inherited from NetBoxModel)."""
        tags = create_tags(["important", "wifi"])
        instance = InterfaceProfile.objects.first()
        instance.tags.add(*tags)
        instance.save()

        self.assertEqual(instance.tags.count(), 2)
        self.assertIn(tags[0], instance.tags.all())

    def test_filter_by_name(self):
        """Test filtering records by name."""
        results = InterfaceProfile.objects.filter(name__startswith="Profile")
        self.assertGreaterEqual(results.count(), 3)


class InterfaceProfileValidationTestCase(PluginModelTestCase):
    """Test InterfaceProfile field validation."""

    def test_name_max_length(self):
        """Test that names exceeding 100 characters are rejected."""
        long_name = "x" * 101

        with self.assertRaises(ValidationError):
            instance = InterfaceProfile(name=long_name)
            instance.full_clean()

    def test_name_required(self):
        """Test that name is required."""
        with self.assertRaises(ValidationError):
            instance = InterfaceProfile(name="")
            instance.full_clean()


class InterfaceTemplateTestCase(PluginModelTestCase):
    """Test InterfaceTemplate model."""

    @classmethod
    def setUpTestData(cls):
        cls.profile = InterfaceProfile.objects.create(
            name="Template Profile",
            description="",
        )
        cls.site_group = SiteGroup.objects.create(name="SG-1", slug="sg-1")

    def test_create_interface_template(self):
        """Test creating an InterfaceTemplate instance with optional fields."""
        template = InterfaceTemplate.objects.create(
            interface_profile=self.profile,
            site_group=self.site_group,
            name="Access Port Template",
            description="",
            speed=1000,
            duplex="full",
            mtu=1500,
            mode="access",
            enabled=True,
            poe_mode="power-supply",
            untagged_vlan_vid=10,
            tagged_vlans_vids=[20, 30],
        )

        self.assertEqual(template.name, "Access Port Template")
        self.assertEqual(template.interface_profile, self.profile)
        self.assertEqual(template.site_group, self.site_group)
        self.assertEqual(template.untagged_vlan_vid, 10)
        self.assertEqual(template.tagged_vlans_vids, [20, 30])

    def test_profile_device_roles_assignment(self):
        """Test assigning device role scopes to InterfaceProfile."""
        role = DeviceRole.objects.create(name="Role-A", slug="role-a")
        profile = InterfaceProfile.objects.create(name="Scoped Profile", description="")
        profile.device_roles.add(role)

        self.assertEqual(profile.device_roles.count(), 1)
        self.assertIn(role, profile.device_roles.all())

    def test_vlan_resolution_prefers_site_vlan(self):
        """Test VID resolution prefers VLAN explicitly assigned to the site."""
        site_group = SiteGroup.objects.create(name="SG-Resolve-1", slug="sg-resolve-1")
        site = Site.objects.create(name="Site-Resolve-1", slug="site-resolve-1", group=site_group)

        # Site-scoped VLAN in site-specific group
        site_ct = ContentType.objects.get_for_model(Site)
        site_vlan_group = VLANGroup.objects.create(
            name="VG-Site-1",
            slug="vg-site-1",
            scope_type=site_ct,
            scope_id=site.pk,
        )
        site_vlan = VLAN.objects.create(name="VLAN10-Site", vid=10, site=site, group=site_vlan_group)

        # SiteGroup-scoped VLAN with same VID; should lose to site VLAN
        site_group_ct = ContentType.objects.get_for_model(SiteGroup)
        site_group_vlan_group = VLANGroup.objects.create(
            name="VG-SG-1",
            slug="vg-sg-1",
            scope_type=site_group_ct,
            scope_id=site_group.pk,
        )
        VLAN.objects.create(name="VLAN10-SG", vid=10, group=site_group_vlan_group)

        template = InterfaceTemplate.objects.create(
            interface_profile=self.profile,
            name="Resolve Template",
            untagged_vlan_vid=10,
            tagged_vlans_vids=[10],
        )

        resolved_untagged = template.resolve_untagged_vlan(site)
        resolved_tagged = template.resolve_tagged_vlans(site)

        self.assertIsNotNone(resolved_untagged)
        self.assertEqual(resolved_untagged.pk, site_vlan.pk)
        self.assertEqual(len(resolved_tagged), 1)
        self.assertEqual(resolved_tagged[0].pk, site_vlan.pk)


class InterfaceProfileAssignmentSignalTestCase(PluginModelTestCase):
    """Test automatic template application on interface profile assignment."""

    @classmethod
    def setUpTestData(cls):
        cls.profile = InterfaceProfile.objects.create(name="Signal Profile", description="")
        cls.site_group = SiteGroup.objects.create(name="SG-Signal", slug="sg-signal")
        cls.site = Site.objects.create(name="Site-Signal", slug="site-signal", group=cls.site_group)

        manufacturer = Manufacturer.objects.create(name="Manufacturer-Signal", slug="manufacturer-signal")
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model="DeviceType-Signal",
            slug="devicetype-signal",
        )
        role = DeviceRole.objects.create(name="Role-Signal", slug="role-signal")

        cls.device = Device.objects.create(
            name="Device-Signal",
            site=cls.site,
            device_type=device_type,
            role=role,
        )
        cls.interface = Interface.objects.create(
            device=cls.device,
            name="eth0",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            enabled=False,
        )

        site_ct = ContentType.objects.get_for_model(Site)
        cls.site_vlan_group = VLANGroup.objects.create(
            name="VG-Signal-Site",
            slug="vg-signal-site",
            scope_type=site_ct,
            scope_id=cls.site.pk,
        )
        cls.untagged_vlan = VLAN.objects.create(
            name="VLAN10-Signal",
            vid=10,
            site=cls.site,
            group=cls.site_vlan_group,
        )
        cls.tagged_vlan = VLAN.objects.create(
            name="VLAN20-Signal",
            vid=20,
            site=cls.site,
            group=cls.site_vlan_group,
        )

    def test_assignment_applies_matching_template_attributes(self):
        """Assigning a profile should apply matching template attributes."""
        InterfaceTemplate.objects.create(
            interface_profile=self.profile,
            name="Global Access Template",
            enabled=True,
            speed=1000,
            duplex="full",
            mtu=9000,
            mode=InterfaceModeChoices.MODE_ACCESS,
            poe_mode="power-supply",
            untagged_vlan_vid=10,
            tagged_vlans_vids=[20],
        )

        from ..models import InterfaceProfileAssignment

        InterfaceProfileAssignment.objects.create(
            interface=self.interface,
            interface_profile=self.profile,
        )

        self.interface.refresh_from_db()
        self.assertTrue(self.interface.enabled)
        self.assertEqual(self.interface.speed, 1000)
        self.assertEqual(self.interface.duplex, "full")
        self.assertEqual(self.interface.mtu, 9000)
        self.assertEqual(self.interface.mode, InterfaceModeChoices.MODE_ACCESS)
        self.assertEqual(self.interface.poe_mode, "power-supply")
        self.assertEqual(self.interface.untagged_vlan_id, self.untagged_vlan.pk)
        self.assertEqual(set(self.interface.tagged_vlans.values_list("pk", flat=True)), {self.tagged_vlan.pk})

    def test_assignment_uses_global_template_when_no_site_group_template_exists(self):
        """A global template should still apply even when its name differs from the interface."""
        InterfaceTemplate.objects.create(
            interface_profile=self.profile,
            name="Global Access Template",
            enabled=True,
            speed=1000,
        )

        from ..models import InterfaceProfileAssignment

        InterfaceProfileAssignment.objects.create(
            interface=self.interface,
            interface_profile=self.profile,
        )

        self.interface.refresh_from_db()
        self.assertTrue(self.interface.enabled)
        self.assertEqual(self.interface.speed, 1000)
