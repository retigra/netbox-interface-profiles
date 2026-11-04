"""
Test cases for interface profiles models.
"""

import hashlib
from typing import Any, cast

from core.models import AutoSyncRecord, DataFile, DataSource, ObjectType
from dcim.choices import InterfaceModeChoices, InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Platform, Site, SiteGroup
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils import timezone
from extras.models import ConfigTemplate
from ipam.models import VLAN, VLANGroup

from ..forms import InterfaceTemplateForm, ProfileConfigTemplateForm
from ..models import InterfaceRole, InterfaceRoleAssignment, InterfaceTemplate, ProfileConfigTemplate, RoleGroup
from ..testing import PluginModelTestCase
from ..testing.utils import create_tags, get_random_string


class InterfaceRoleTestCase(PluginModelTestCase):
    """Test InterfaceRole model."""

    @classmethod
    def setUpTestData(cls):
        """Create three InterfaceRole records."""
        InterfaceRole.objects.create(
            name="Role 1",
            description="First role",
        )
        InterfaceRole.objects.create(
            name="Role 2",
            description="Second role",
        )
        InterfaceRole.objects.create(
            name="Role 3",
            description="",
        )

    def test_create_interface_role(self):
        """Test creating an InterfaceRole instance."""
        name = f"Role {get_random_string(10)}"
        instance = InterfaceRole.objects.create(
            name=name,
            description="A test role",
        )

        self.assertEqual(instance.name, name)
        self.assertEqual(instance.description, "A test role")
        self.assertIsNotNone(instance.pk)

    def test_create_without_description(self):
        """Test that description is optional (blank allowed)."""
        instance = InterfaceRole.objects.create(
            name=f"No Desc {get_random_string(6)}",
        )

        self.assertEqual(instance.description, "")

    def test_str_representation(self):
        """Test InterfaceRole string representation returns name."""
        instance = InterfaceRole.objects.first()
        self.assertEqual(str(instance), instance.name)

    def test_absolute_url_contains_pk(self):
        """Test get_absolute_url includes the instance PK."""
        instance = InterfaceRole.objects.first()
        url = instance.get_absolute_url()

        self.assertIsNotNone(url)
        self.assertIn(str(instance.pk), url)

    def test_default_ordering(self):
        """Test that instances are ordered by name."""
        instances = list(InterfaceRole.objects.all())
        names = [i.name for i in instances]
        self.assertEqual(names, sorted(names))

    def test_model_to_dict(self):
        """Test model_to_dict helper includes expected keys."""
        instance = InterfaceRole.objects.first()
        data = self.model_to_dict(instance)

        self.assertIn("name", data)
        self.assertEqual(data["name"], instance.name)
        self.assertIn("id", data)

    def test_instance_equal(self):
        """Test assertInstanceEqual helper with matching data."""
        instance = InterfaceRole.objects.first()
        self.assertInstanceEqual(
            instance,
            {"name": instance.name, "id": instance.pk},
        )

    def test_interface_role_with_tags(self):
        """Test InterfaceRole supports tags (inherited from NetBoxModel)."""
        tags = create_tags(["important", "wifi"])
        instance = InterfaceRole.objects.first()
        instance.tags.add(*tags)
        instance.save()

        self.assertEqual(instance.tags.count(), 2)
        self.assertIn(tags[0], instance.tags.all())

    def test_filter_by_name(self):
        """Test filtering records by name."""
        results = InterfaceRole.objects.filter(name__startswith="Role")
        self.assertGreaterEqual(results.count(), 3)


class InterfaceRoleValidationTestCase(PluginModelTestCase):
    """Test InterfaceRole field validation."""

    def test_name_max_length(self):
        """Test that names exceeding 100 characters are rejected."""
        long_name = "x" * 101

        with self.assertRaises(ValidationError):
            instance = InterfaceRole(name=long_name)
            instance.full_clean()

    def test_name_required(self):
        """Test that name is required."""
        with self.assertRaises(ValidationError):
            instance = InterfaceRole(name="")
            instance.full_clean()


class InterfaceTemplateTestCase(PluginModelTestCase):
    """Test InterfaceTemplate model."""

    @classmethod
    def setUpTestData(cls):
        cls.role = InterfaceRole.objects.create(
            name="Template Role",
            description="",
        )
        cls.site_group = SiteGroup.objects.create(name="SG-1", slug="sg-1")

    def test_create_interface_template(self):
        """Test creating an InterfaceTemplate instance with optional fields."""
        template = InterfaceTemplate.objects.create(
            interface_role=self.role,
            scope=self.site_group,
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
        self.assertEqual(template.interface_role, self.role)
        self.assertEqual(template.scope, self.site_group)
        self.assertEqual(template.untagged_vlan_vid, 10)
        self.assertEqual(template.tagged_vlans_vids, [20, 30])

    def test_role_device_roles_assignment(self):
        """Test assigning device role scopes to InterfaceRole."""
        device_role = DeviceRole.objects.create(name="Role-A", slug="role-a")
        role = InterfaceRole.objects.create(name="Scoped Role", description="")
        role.device_roles.add(device_role)

        self.assertEqual(role.device_roles.count(), 1)
        self.assertIn(device_role, role.device_roles.all())

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
            interface_role=self.role,
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

    def test_set_null_requires_empty_value(self):
        """Clearing an attribute and setting a value for it at the same time is rejected."""
        template = InterfaceTemplate(
            interface_role=self.role,
            name="Conflicting Template",
            speed=1000,
            set_null_speed=True,
            set_null_mtu=True,
        )

        with self.assertRaises(ValidationError) as context:
            template.full_clean()

        self.assertEqual(set(context.exception.error_dict), {"set_null_speed"})

    def test_set_null_mode_rejects_vlans(self):
        """An interface without a mode cannot carry VLANs, so clearing the mode excludes them."""
        template = InterfaceTemplate(
            interface_role=self.role,
            name="Modeless Template",
            set_null_mode=True,
            tagged_vlans_vids=[20],
        )

        with self.assertRaises(ValidationError) as context:
            template.full_clean()

        self.assertEqual(set(context.exception.error_dict), {"set_null_mode"})

    def test_template_form_stores_blank_choices_as_null(self):
        """Empty choices from the edit form are stored as None, so they leave the interface unchanged."""
        form = InterfaceTemplateForm(
            data={
                "interface_role": self.role.pk,
                "name": "Form Template",
                "duplex": "",
                "mode": "",
                "poe_mode": "",
                "set_null_duplex": "on",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        template = form.save()
        self.assertIsNone(template.duplex)
        self.assertIsNone(template.mode)
        self.assertIsNone(template.poe_mode)
        self.assertTrue(template.set_null_duplex)
        self.assertFalse(template.set_null_mode)


class InterfaceRoleAssignmentSignalTestCase(PluginModelTestCase):
    """Test automatic template application on interface role assignment."""

    @classmethod
    def setUpTestData(cls):
        cls.role = InterfaceRole.objects.create(name="Signal Role", description="")
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
        """Assigning a role should apply matching template attributes."""
        InterfaceTemplate.objects.create(
            interface_role=self.role,
            name="Global Access Template",
            enabled=True,
            speed=1000,
            duplex="full",
            mtu=9000,
            mode=InterfaceModeChoices.MODE_ACCESS,
            poe_mode="pse",
            untagged_vlan_vid=10,
            tagged_vlans_vids=[20],
        )

        InterfaceRoleAssignment.objects.create(
            interface=self.interface,
            interface_role=self.role,
        )

        self.interface.refresh_from_db()
        self.assertTrue(self.interface.enabled)
        self.assertEqual(self.interface.speed, 1000)
        self.assertEqual(self.interface.duplex, "full")
        self.assertEqual(self.interface.mtu, 9000)
        self.assertEqual(self.interface.mode, InterfaceModeChoices.MODE_ACCESS)
        self.assertEqual(self.interface.poe_mode, "pse")
        self.assertEqual(self.interface.untagged_vlan_id, self.untagged_vlan.pk)
        self.assertEqual(set(self.interface.tagged_vlans.values_list("pk", flat=True)), {self.tagged_vlan.pk})

    def test_assignment_uses_global_template_when_no_site_group_template_exists(self):
        """A global template should still apply even when its name differs from the interface."""
        InterfaceTemplate.objects.create(
            interface_role=self.role,
            name="Global Access Template",
            enabled=True,
            speed=1000,
        )

        InterfaceRoleAssignment.objects.create(
            interface=self.interface,
            interface_role=self.role,
        )

        self.interface.refresh_from_db()
        self.assertTrue(self.interface.enabled)
        self.assertEqual(self.interface.speed, 1000)

    def _configure_interface(self):
        self.interface.speed = 1000000
        self.interface.duplex = "full"
        self.interface.mtu = 9000
        self.interface.mode = InterfaceModeChoices.MODE_ACCESS
        self.interface.poe_mode = "pse"
        self.interface.untagged_vlan = self.untagged_vlan
        self.interface.save()

    def test_assignment_leaves_empty_template_attributes_unchanged(self):
        """Empty template attributes, including blank choices, do not change the interface."""
        self._configure_interface()
        InterfaceTemplate.objects.create(
            interface_role=self.role,
            name="Empty Template",
            enabled=True,
            duplex="",
            mode="",
            poe_mode="",
        )

        InterfaceRoleAssignment.objects.create(interface=self.interface, interface_role=self.role)

        self.interface.refresh_from_db()
        self.assertEqual(self.interface.speed, 1000000)
        self.assertEqual(self.interface.duplex, "full")
        self.assertEqual(self.interface.mtu, 9000)
        self.assertEqual(self.interface.mode, InterfaceModeChoices.MODE_ACCESS)
        self.assertEqual(self.interface.poe_mode, "pse")
        self.assertEqual(self.interface.untagged_vlan_id, self.untagged_vlan.pk)

    def test_assignment_clears_set_null_attributes(self):
        """Template attributes marked set_null are cleared on the interface."""
        self._configure_interface()
        InterfaceTemplate.objects.create(
            interface_role=self.role,
            name="Clearing Template",
            enabled=True,
            mode=InterfaceModeChoices.MODE_ACCESS,
            set_null_speed=True,
            set_null_duplex=True,
            set_null_mtu=True,
            set_null_poe_mode=True,
            set_null_untagged_vlan_vid=True,
        )

        InterfaceRoleAssignment.objects.create(interface=self.interface, interface_role=self.role)

        self.interface.refresh_from_db()
        self.assertIsNone(self.interface.speed)
        self.assertIsNone(self.interface.duplex)
        self.assertIsNone(self.interface.mtu)
        self.assertEqual(self.interface.mode, InterfaceModeChoices.MODE_ACCESS)
        self.assertIsNone(self.interface.poe_mode)
        self.assertIsNone(self.interface.untagged_vlan)

    def test_assignment_clears_mode(self):
        """Clearing the mode also removes the untagged VLAN, as NetBox requires a mode for VLANs."""
        self._configure_interface()
        InterfaceTemplate.objects.create(
            interface_role=self.role,
            name="Clear Mode Template",
            enabled=True,
            set_null_mode=True,
        )

        InterfaceRoleAssignment.objects.create(interface=self.interface, interface_role=self.role)

        self.interface.refresh_from_db()
        self.assertIsNone(self.interface.mode)
        self.assertIsNone(self.interface.untagged_vlan)
        self.assertEqual(self.interface.mtu, 9000)


class RoleGroupTestCase(PluginModelTestCase):
    """Test RoleGroup model behaviour."""

    def test_deleting_group_ungroups_roles(self):
        group = RoleGroup.objects.create(name="Trunk", slug="trunk")
        role = InterfaceRole.objects.create(name="Uplink Trunk", group=group)

        group.delete()

        role.refresh_from_db()
        self.assertIsNone(role.group)


class ProfileConfigTemplateTestCase(PluginModelTestCase):
    """Test ProfileConfigTemplate resolution, rendering and data synchronization."""

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name="Config Site", slug="config-site")
        manufacturer = Manufacturer.objects.create(name="Config Manufacturer", slug="config-manufacturer")
        cls.device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="Config Model", slug="config-model"
        )
        cls.other_device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="Other Model", slug="other-model"
        )
        cls.platform = Platform.objects.create(name="Config Platform", slug="config-platform")
        cls.other_platform = Platform.objects.create(name="Other Platform", slug="other-platform")
        device_role = DeviceRole.objects.create(name="Config Device Role", slug="config-device-role")
        cls.device = Device.objects.create(
            name="Config Device",
            site=site,
            device_type=cls.device_type,
            role=device_role,
            platform=cls.platform,
        )
        cls.interface = Interface.objects.create(
            device=cls.device, name="eth0", type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        cls.role = InterfaceRole.objects.create(name="Config Role")
        InterfaceRoleAssignment.objects.create(interface=cls.interface, interface_role=cls.role)
        cls.tags = create_tags(["Device Tag", "Interface Tag", "Other Tag"])

    def create_template(self, name: str, **kwargs) -> ProfileConfigTemplate:
        kwargs.setdefault("interface_role", self.role)
        kwargs.setdefault("platform", self.platform)
        kwargs.setdefault("template_code", f"! {name}")
        device_tags = kwargs.pop("device_tags", ())
        interface_tags = kwargs.pop("interface_tags", ())
        template = ProfileConfigTemplate.objects.create(name=name, **kwargs)
        template.device_tags.set(device_tags)
        template.interface_tags.set(interface_tags)
        return template

    def matching_names(self) -> list[str]:
        return [template.name for template in ProfileConfigTemplate.objects.for_interface(self.interface)]

    def test_for_interface_matches_role_platform_and_device_type(self):
        self.create_template("Platform Default")
        self.create_template("Device Type", device_type=self.device_type)
        self.create_template("Other Device Type", device_type=self.other_device_type)
        self.create_template("Other Platform", platform=self.other_platform)
        self.create_template("Other Role", interface_role=InterfaceRole.objects.create(name="Other Role"))

        self.assertCountEqual(self.matching_names(), ["Platform Default", "Device Type"])

    def test_for_interface_requires_all_tags(self):
        device_tag, interface_tag, other_tag = self.tags
        self.device.tags.add(device_tag)
        self.interface.tags.add(interface_tag)
        self.create_template("Device Tagged", device_tags=[device_tag])
        self.create_template("Interface Tagged", interface_tags=[interface_tag])
        self.create_template("Partially Tagged", interface_tags=[interface_tag, other_tag])
        self.create_template("Device Tag On Interface", interface_tags=[device_tag])

        self.assertCountEqual(self.matching_names(), ["Device Tagged", "Interface Tagged"])

    def test_for_interface_orders_by_weight(self):
        self.create_template("Low", weight=100)
        self.create_template("High", weight=2000)
        self.create_template("Default")

        self.assertEqual(self.matching_names(), ["High", "Default", "Low"])

    def test_for_interface_without_role_or_platform(self):
        self.create_template("Platform Default")
        unassigned = Interface.objects.create(device=self.device, name="eth1", type=InterfaceTypeChoices.TYPE_1GE_FIXED)

        self.assertFalse(ProfileConfigTemplate.objects.for_interface(unassigned).exists())
        self.assertEqual(
            list(ProfileConfigTemplate.objects.for_interface(unassigned, self.role).values_list("name", flat=True)),
            ["Platform Default"],
        )

        self.device.platform = None
        self.device.save()
        self.interface.refresh_from_db()
        self.assertFalse(ProfileConfigTemplate.objects.for_interface(self.interface).exists())

    def test_in_scope_ignores_role(self):
        device_tag, interface_tag, other_tag = self.tags
        self.interface.tags.add(interface_tag)
        self.create_template("Platform Default")
        self.create_template("Other Role", interface_role=InterfaceRole.objects.create(name="Other Role"))
        self.create_template("Other Platform", platform=self.other_platform)
        self.create_template("Other Tag", device_tags=[other_tag])
        self.create_template("Interface Tagged", interface_tags=[interface_tag])
        unassigned = Interface.objects.create(device=self.device, name="eth1", type=InterfaceTypeChoices.TYPE_1GE_FIXED)

        self.assertCountEqual(
            ProfileConfigTemplate.objects.in_scope(self.interface).values_list("name", flat=True),
            ["Platform Default", "Other Role", "Interface Tagged"],
        )
        self.assertCountEqual(
            ProfileConfigTemplate.objects.in_scope(unassigned).values_list("name", flat=True),
            ["Platform Default", "Other Role"],
        )

    def test_render_does_not_escape(self):
        template = self.create_template("Render", template_code="interface {{ interface.name }}\n description {{ x }}")

        self.assertEqual(
            template.render({"interface": self.interface, "x": "<a & b>"}), "interface eth0\n description <a & b>"
        )

    def test_interface_config_render_from_device_template(self):
        self.create_template("Render", template_code="description {{ device.name }} {{ interface.name }} {{ vlan }}")
        Interface.objects.create(device=self.device, name="eth1", type=InterfaceTypeChoices.TYPE_1GE_FIXED)
        device_template = ConfigTemplate.objects.create(
            name="Device",
            template_code=(
                "{% for interface in device.interfaces.order_by('name') %}"
                "interface {{ interface.name }}: {{ interface_config_render(interface, vlan=10) }}\n"
                "{% endfor %}"
            ),
        )

        self.assertEqual(
            device_template.render({"device": self.device}),
            "interface eth0: description Config Device eth0 10\ninterface eth1: \n",
        )

    def test_interface_role_get_from_device_template(self):
        self.create_template("Render")
        Interface.objects.create(device=self.device, name="eth1", type=InterfaceTypeChoices.TYPE_1GE_FIXED)
        device_template = ConfigTemplate.objects.create(
            name="Device",
            template_code=(
                "{% for interface in device.interfaces.order_by('name') %}"
                "{% set role = interface_role_get(interface) %}"
                "{{ interface.name }}: {{ role.name if role else 'none' }}\n"
                "{% endfor %}"
            ),
        )

        self.assertEqual(device_template.render({"device": self.device}), "eth0: Config Role\neth1: none\n")

    def test_environment_params_are_validated(self):
        template = self.create_template("Params", environment_params={"loader": "x"})

        with self.assertRaises(ValidationError):
            template.full_clean()

    def test_sync_from_data_file(self):
        data_source = DataSource.objects.create(name="Templates", type="local", source_url="file:///tmp/templates")
        content = b"interface {{ interface.name }}"
        data_file = DataFile.objects.create(
            source=data_source,
            path="access.j2",
            last_updated=timezone.now(),
            size=len(content),
            hash=hashlib.sha256(content).hexdigest(),
            data=content,
        )
        form = ProfileConfigTemplateForm(
            data={
                "name": "Synced",
                "interface_role": self.role.pk,
                "platform": self.platform.pk,
                "weight": 1000,
                "data_source": data_source.pk,
                "data_file": data_file.pk,
                "auto_sync_enabled": True,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        template = form.save()

        self.assertEqual(template.template_code, "interface {{ interface.name }}")
        self.assertEqual(template.data_source, data_source)
        self.assertEqual(template.data_path, "access.j2")
        self.assertIsNotNone(template.data_synced)
        auto_sync_records = cast(Any, AutoSyncRecord).objects.filter(
            object_type=ObjectType.objects.get_for_model(ProfileConfigTemplate), object_id=template.pk
        )
        self.assertTrue(auto_sync_records.exists())
