"""
Test cases for interface profiles REST API.
"""

from dcim.choices import InterfaceModeChoices, InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Platform, Site
from django.urls import reverse
from extras.models import ConfigContext
from ipam.models import VLAN

from ..models import InterfaceRole, InterfaceRoleAssignment, InterfaceTemplate, ProfileConfigTemplate, RoleGroup
from ..testing import PluginAPITestCase
from ..testing.utils import create_tags, disable_warnings, get_random_string


class InterfaceRoleAPITestCase(PluginAPITestCase):
    """Test InterfaceRole API endpoints."""

    @classmethod
    def setUpTestData(cls):
        """Create three InterfaceRole instances."""
        InterfaceRole.objects.create(name="API Role 1", description="First")
        InterfaceRole.objects.create(name="API Role 2", description="Second")
        InterfaceRole.objects.create(name="API Role 3", description="")

    def setUp(self):
        """Set up URL names for InterfaceRole endpoints."""
        super().setUp()
        self.list_url_name = "plugins-api:interface_profiles-api:interfacerole-list"
        self.detail_url_name = "plugins-api:interface_profiles-api:interfacerole-detail"

    def test_list_interface_roles(self):
        """Test GET request returns all InterfaceRole objects."""
        self.add_permissions("interface_profiles.view_interfacerole")

        url = self._get_list_url()
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertEqual(response.data["count"], 3)
        self.assertIn("results", response.data)

    def test_list_interface_roles_without_permission(self):
        """Test GET request without permission returns 403."""
        url = self._get_list_url()

        with disable_warnings("django.request"):
            response = self.client.get(url)
            self.assertHttpStatus(response, 403)

    def test_get_interface_role(self):
        """Test GET request for a single InterfaceRole."""
        self.add_permissions("interface_profiles.view_interfacerole")

        instance = InterfaceRole.objects.first()
        url = self._get_detail_url(instance)
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertEqual(response.data["id"], instance.pk)
        self.assertEqual(response.data["name"], instance.name)

    def test_create_interface_role(self):
        """Test POST request creates an InterfaceRole."""
        self.add_permissions("interface_profiles.add_interfacerole")

        url = self._get_list_url()
        name = f"API Created {get_random_string(10)}"
        data = {
            "name": name,
            "description": "Created via API",
        }

        response = self.client.post(url, data, format="json")
        self.assertHttpStatus(response, 201)

        instance = InterfaceRole.objects.get(name=name)
        self.assertEqual(instance.description, "Created via API")
        self.assertEqual(response.data["id"], instance.pk)

    def test_create_interface_role_with_blank_description(self):
        """Test POST request accepts a blank optional description."""
        self.add_permissions("interface_profiles.add_interfacerole")

        url = self._get_list_url()
        data = {
            "name": f"No Desc {get_random_string(6)}",
            "description": "",
        }

        response = self.client.post(url, data, format="json")
        self.assertHttpStatus(response, 201)
        self.assertEqual(response.data["description"], "")

    def test_create_interface_role_without_permission(self):
        """Test POST request without permission returns 403."""
        url = self._get_list_url()

        with disable_warnings("django.request"):
            response = self.client.post(
                url,
                {"name": "Test", "description": ""},
                format="json",
            )
            self.assertHttpStatus(response, 403)

    def test_update_interface_role(self):
        """Test PATCH request updates an InterfaceRole name."""
        self.add_permissions("interface_profiles.change_interfacerole")

        instance = InterfaceRole.objects.first()
        url = self._get_detail_url(instance)
        new_name = f"Updated {get_random_string(10)}"

        response = self.client.patch(url, {"name": new_name}, format="json")
        self.assertHttpStatus(response, 200)

        instance.refresh_from_db()
        self.assertEqual(instance.name, new_name)

    def test_update_interface_role_without_permission(self):
        """Test PATCH request without permission returns 403."""
        instance = InterfaceRole.objects.first()
        url = self._get_detail_url(instance)

        with disable_warnings("django.request"):
            response = self.client.patch(url, {"name": "Test"}, format="json")
            self.assertHttpStatus(response, 403)

    def test_delete_interface_role(self):
        """Test DELETE request removes an InterfaceRole."""
        self.add_permissions("interface_profiles.delete_interfacerole")

        instance = InterfaceRole.objects.last()
        pk = instance.pk
        url = self._get_detail_url(instance)

        response = self.client.delete(url)
        self.assertHttpStatus(response, 204)
        self.assertFalse(InterfaceRole.objects.filter(pk=pk).exists())

    def test_delete_interface_role_without_permission(self):
        """Test DELETE request without permission returns 403."""
        instance = InterfaceRole.objects.first()
        url = self._get_detail_url(instance)

        with disable_warnings("django.request"):
            response = self.client.delete(url)
            self.assertHttpStatus(response, 403)

    def test_options_endpoint(self):
        """Test OPTIONS request on the list endpoint succeeds."""
        self.add_permissions("interface_profiles.view_interfacerole")

        url = self._get_list_url()
        response = self.client.options(url)
        self.assertHttpStatus(response, 200)


class InterfaceRoleAPIValidationTestCase(PluginAPITestCase):
    """Test InterfaceRole API input validation."""

    def setUp(self):
        """Grant add permission and set URL name."""
        super().setUp()
        self.add_permissions("interface_profiles.add_interfacerole")
        self.list_url_name = "plugins-api:interface_profiles-api:interfacerole-list"

    def test_create_with_missing_name(self):
        """Test that missing name is rejected with HTTP 400."""
        url = self._get_list_url()
        data = {"name": "", "description": "Some description"}

        response = self.client.post(url, data, format="json")
        self.assertHttpStatus(response, 400)
        self.assertIn("name", response.data)


class RoleGroupAPITestCase(PluginAPITestCase):
    """Test RoleGroup API endpoints and the group field on InterfaceRole."""

    @classmethod
    def setUpTestData(cls):
        cls.group = RoleGroup.objects.create(name="Access", slug="access")

    def setUp(self):
        super().setUp()
        self.list_url_name = "plugins-api:interface_profiles-api:rolegroup-list"
        self.detail_url_name = "plugins-api:interface_profiles-api:rolegroup-detail"

    def test_list_role_groups(self):
        self.add_permissions("interface_profiles.view_rolegroup")

        response = self.client.get(self._get_list_url())

        self.assertHttpStatus(response, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["slug"], "access")

    def test_create_role_group(self):
        self.add_permissions("interface_profiles.add_rolegroup")

        response = self.client.post(self._get_list_url(), {"name": "Trunk", "slug": "trunk"}, format="json")

        self.assertHttpStatus(response, 201)
        self.assertTrue(RoleGroup.objects.filter(slug="trunk").exists())

    def test_assign_group_to_interface_role(self):
        self.add_permissions("interface_profiles.add_interfacerole")

        url = reverse("plugins-api:interface_profiles-api:interfacerole-list")
        response = self.client.post(url, {"name": "Access VLAN 10", "group": self.group.pk}, format="json")

        self.assertHttpStatus(response, 201)
        self.assertEqual(response.data["group"]["id"], self.group.pk)
        self.assertEqual(InterfaceRole.objects.get(name="Access VLAN 10").group, self.group)


class ProfileConfigTemplateAPITestCase(PluginAPITestCase):
    """Test ProfileConfigTemplate API endpoints."""

    @classmethod
    def setUpTestData(cls):
        cls.role = InterfaceRole.objects.create(name="API Config Role")
        cls.platform = Platform.objects.create(name="API Platform", slug="api-platform")
        cls.tags = create_tags(["API Device Tag", "API Interface Tag"])

    def setUp(self):
        super().setUp()
        self.list_url_name = "plugins-api:interface_profiles-api:profileconfigtemplate-list"
        self.detail_url_name = "plugins-api:interface_profiles-api:profileconfigtemplate-detail"

    def test_create_profile_config_template(self):
        """Test POST request creates a template with its scope."""
        self.add_permissions("interface_profiles.add_profileconfigtemplate")
        device_tag, interface_tag = self.tags

        data = {
            "name": "API Template",
            "interface_role": self.role.pk,
            "platform": self.platform.pk,
            "device_tags": [device_tag.pk],
            "interface_tags": [interface_tag.pk],
            "weight": 500,
            "template_code": "interface {{ interface.name }}",
            "environment_params": {"trim_blocks": True},
        }
        response = self.client.post(self._get_list_url(), data, format="json")
        self.assertHttpStatus(response, 201)

        instance = ProfileConfigTemplate.objects.get(name="API Template")
        self.assertEqual(instance.interface_role, self.role)
        self.assertEqual(instance.weight, 500)
        self.assertEqual(list(instance.device_tags.all()), [device_tag])
        self.assertEqual(list(instance.interface_tags.all()), [interface_tag])
        self.assertEqual(response.data["interface_role"]["id"], self.role.pk)
        self.assertEqual(response.data["device_tags"][0]["slug"], device_tag.slug)

    def test_create_with_invalid_environment_params(self):
        """Test environment parameters are validated as for NetBox config templates."""
        self.add_permissions("interface_profiles.add_profileconfigtemplate")

        data = {
            "name": "API Invalid Template",
            "interface_role": self.role.pk,
            "platform": self.platform.pk,
            "template_code": "!",
            "environment_params": {"loader": "x"},
        }
        with disable_warnings("django.request"):
            response = self.client.post(self._get_list_url(), data, format="json")
        self.assertHttpStatus(response, 400)

    def test_sync_requires_sync_permission(self):
        """Test the /sync/ action is guarded by the sync permission."""
        instance = ProfileConfigTemplate.objects.create(
            name="API Sync Template", interface_role=self.role, platform=self.platform, template_code="!"
        )
        url = reverse("plugins-api:interface_profiles-api:profileconfigtemplate-sync", kwargs={"pk": instance.pk})

        with disable_warnings("django.request"):
            self.assertHttpStatus(self.client.post(url, format="json"), 403)

        self.add_permissions("interface_profiles.sync_profileconfigtemplate")
        self.assertHttpStatus(self.client.post(url, format="json"), 200)


class InterfaceConfigAPITestMixin:
    """A device with a role assigned to one of its interfaces, with an interface and config template."""

    @classmethod
    def setUpTestData(cls):
        cls.group = RoleGroup.objects.create(name="Access", slug="access")
        cls.role = InterfaceRole.objects.create(name="Workstation", group=cls.group)
        cls.platform = Platform.objects.create(name="IOS", slug="ios")
        site = Site.objects.create(name="Site-API", slug="site-api")
        manufacturer = Manufacturer.objects.create(name="Manufacturer-API", slug="manufacturer-api")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Type-API", slug="type-api")
        device_role = DeviceRole.objects.create(name="Role-API", slug="role-api")
        cls.device = Device.objects.create(
            name="sw01", site=site, device_type=device_type, role=device_role, platform=cls.platform
        )
        cls.other_device = Device.objects.create(
            name="sw02", site=site, device_type=device_type, role=device_role, platform=cls.platform
        )
        VLAN.objects.create(name="Users", vid=100, site=site)

        cls.interface = Interface.objects.create(
            device=cls.device, name="Gi1", type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        cls.unassigned_interface = Interface.objects.create(
            device=cls.device, name="Gi2", type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        cls.other_interface = Interface.objects.create(
            device=cls.other_device, name="Gi1", type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )

        cls.interface_template = InterfaceTemplate.objects.create(
            interface_role=cls.role, name="Default", mode=InterfaceModeChoices.MODE_ACCESS, untagged_vlan_vid=100
        )
        cls.config_template = ProfileConfigTemplate.objects.create(
            name="IOS access",
            interface_role=cls.role,
            platform=cls.platform,
            template_code=(
                "interface {{ interface.name }}\n"
                " switchport access vlan {{ interface.untagged_vlan.vid }}\n"
                " ntp {{ ntp_server }}"
            ),
        )
        ConfigContext.objects.create(name="NTP", data={"ntp_server": "192.0.2.1"})

        cls.assignment = InterfaceRoleAssignment.objects.create(interface=cls.interface, interface_role=cls.role)
        InterfaceRoleAssignment.objects.create(interface=cls.other_interface, interface_role=cls.role)


class InterfaceRoleAssignmentAPITestCase(InterfaceConfigAPITestMixin, PluginAPITestCase):
    """Test the InterfaceRoleAssignment API endpoint."""

    def setUp(self):
        super().setUp()
        self.list_url_name = "plugins-api:interface_profiles-api:interfaceroleassignment-list"

    def test_filter_by_interface_returns_nested_role(self):
        """Filtering on an interface ID returns its assignment with the role as a nested object."""
        self.add_permissions("interface_profiles.view_interfaceroleassignment")

        response = self.client.get(self._get_list_url(), {"interface_id": self.interface.pk})

        self.assertHttpStatus(response, 200)
        self.assertEqual(response.data["count"], 1)
        result = response.data["results"][0]
        self.assertEqual(result["interface"]["id"], self.interface.pk)
        self.assertEqual(result["interface"]["device"]["name"], "sw01")
        self.assertEqual(result["interface_role"]["id"], self.role.pk)
        self.assertEqual(result["interface_role"]["name"], "Workstation")
        self.assertEqual(result["interface_role"]["group"]["slug"], "access")

    def test_filter_by_device_and_interface_name(self):
        """Assignments can be looked up by device and interface name."""
        self.add_permissions("interface_profiles.view_interfaceroleassignment")

        response = self.client.get(self._get_list_url(), {"device": "sw02", "interface": "Gi1"})

        self.assertHttpStatus(response, 200)
        self.assertEqual([result["interface"]["id"] for result in response.data["results"]], [self.other_interface.pk])

    def test_create_assignment_by_id(self):
        """The interface and role are still written by ID."""
        self.add_permissions("interface_profiles.add_interfaceroleassignment", "dcim.change_interface")

        response = self.client.post(
            self._get_list_url(),
            {"interface": self.unassigned_interface.pk, "interface_role": self.role.pk},
            format="json",
        )

        self.assertHttpStatus(response, 201)
        self.assertEqual(response.data["interface_role"]["name"], "Workstation")
        self.unassigned_interface.refresh_from_db()
        self.assertEqual(self.unassigned_interface.mode, InterfaceModeChoices.MODE_ACCESS)


class InterfaceConfigAPITestCase(InterfaceConfigAPITestMixin, PluginAPITestCase):
    """Test the read-only interface configuration API endpoint."""

    def setUp(self):
        super().setUp()
        self.list_url_name = "plugins-api:interface_profiles-api:interfaceconfig-list"
        self.detail_url_name = "plugins-api:interface_profiles-api:interfaceconfig-detail"

    def test_get_interface_config(self):
        """The detail endpoint returns the role, matching templates and rendered config of an interface."""
        self.add_permissions("dcim.view_interface", "interface_profiles.view_interfaceroleassignment")

        response = self.client.get(self._get_detail_url(self.interface))

        self.assertHttpStatus(response, 200)
        data = response.data
        self.assertEqual(data["id"], self.interface.pk)
        self.assertEqual(data["interface"]["name"], "Gi1")
        self.assertEqual(data["role_assignment"]["id"], self.assignment.pk)
        self.assertEqual(data["interface_role"]["name"], "Workstation")
        self.assertEqual(data["interface_template"]["id"], self.interface_template.pk)
        self.assertEqual(data["config_template"]["id"], self.config_template.pk)
        self.assertEqual(data["config"], "interface Gi1\n switchport access vlan 100\n ntp 192.0.2.1")
        self.assertIsNone(data["config_error"])

    def test_get_interface_without_role(self):
        """An interface without a role is returned with empty role, templates and config."""
        self.add_permissions("dcim.view_interface", "interface_profiles.view_interfaceroleassignment")

        response = self.client.get(self._get_detail_url(self.unassigned_interface))

        self.assertHttpStatus(response, 200)
        for field in ("role_assignment", "interface_role", "interface_template", "config_template", "config"):
            self.assertIsNone(response.data[field], field)

    def test_render_error_is_returned(self):
        """A template that fails to render returns the error instead of the config."""
        self.add_permissions("dcim.view_interface", "interface_profiles.view_interfaceroleassignment")
        self.config_template.template_code = "{{ interface.name | no_such_filter }}"
        self.config_template.save()

        response = self.client.get(self._get_detail_url(self.interface))

        self.assertHttpStatus(response, 200)
        self.assertIsNone(response.data["config"])
        self.assertIn("no_such_filter", response.data["config_error"])

    def test_list_filtered_by_device_and_role(self):
        """The list endpoint supports NetBox's interface filters and filters on the role."""
        self.add_permissions("dcim.view_interface", "interface_profiles.view_interfaceroleassignment")

        response = self.client.get(self._get_list_url(), {"device_id": self.device.pk})
        self.assertHttpStatus(response, 200)
        self.assertEqual(
            {result["id"] for result in response.data["results"]}, {self.interface.pk, self.unassigned_interface.pk}
        )

        response = self.client.get(self._get_list_url(), {"device": "sw01", "has_interface_role": True})
        self.assertEqual([result["id"] for result in response.data["results"]], [self.interface.pk])

        response = self.client.get(self._get_list_url(), {"interface_role": "Workstation"})
        self.assertEqual(
            {result["id"] for result in response.data["results"]}, {self.interface.pk, self.other_interface.pk}
        )

        response = self.client.get(self._get_list_url(), {"interface_role_group": "access", "name": "Gi1"})
        self.assertEqual(response.data["count"], 2)

    def test_brief_mode_skips_rendering(self):
        """Brief mode returns the role without rendering the configuration."""
        self.add_permissions("dcim.view_interface", "interface_profiles.view_interfaceroleassignment")

        response = self.client.get(self._get_detail_url(self.interface), {"brief": True})

        self.assertHttpStatus(response, 200)
        self.assertEqual(set(response.data), {"id", "url", "display", "interface_role"})
        self.assertEqual(response.data["interface_role"]["name"], "Workstation")

    def test_requires_view_interface_permission(self):
        """Viewing interface configuration requires permission to view the interface."""
        self.add_permissions("interface_profiles.view_interfaceroleassignment")

        with disable_warnings("django.request"):
            self.assertHttpStatus(self.client.get(self._get_list_url()), 403)

    def test_role_hidden_without_view_assignment_permission(self):
        """The role is only returned when the user may view the interface's role assignment."""
        self.add_permissions("dcim.view_interface")

        response = self.client.get(self._get_detail_url(self.interface))

        self.assertHttpStatus(response, 200)
        self.assertIsNone(response.data["interface_role"])
        self.assertIsNone(response.data["config"])

    def test_read_only(self):
        """The endpoint does not accept writes."""
        self.add_permissions("dcim.view_interface", "dcim.change_interface")

        with disable_warnings("django.request"):
            response = self.client.patch(self._get_detail_url(self.interface), {"description": "x"}, format="json")
        self.assertIn(response.status_code, (403, 405))


class InterfaceTemplateAPITestCase(PluginAPITestCase):
    """Test the InterfaceTemplate API endpoint."""

    @classmethod
    def setUpTestData(cls):
        cls.role = InterfaceRole.objects.create(name="API Template Role")
        cls.site = Site.objects.create(name="Site-Templates", slug="site-templates")
        cls.global_template = InterfaceTemplate.objects.create(
            interface_role=cls.role, name="Global", mode=InterfaceModeChoices.MODE_TAGGED, tagged_vlans_vids=[10, 20]
        )
        cls.site_template = InterfaceTemplate.objects.create(
            interface_role=cls.role, name="Site", scope=cls.site, mode=InterfaceModeChoices.MODE_ACCESS
        )

    def setUp(self):
        super().setUp()
        self.list_url_name = "plugins-api:interface_profiles-api:interfacetemplate-list"

    def test_filters(self):
        self.add_permissions("interface_profiles.view_interfacetemplate")

        def names(**params):
            response = self.client.get(self._get_list_url(), params)
            self.assertHttpStatus(response, 200)
            return {result["name"] for result in response.data["results"]}

        self.assertEqual(names(scope_site_id=self.site.pk), {"Site"})
        self.assertEqual(names(is_global=True), {"Global"})
        self.assertEqual(names(mode="access"), {"Site"})
        self.assertEqual(names(tagged_vlan_vid=20), {"Global"})
        self.assertEqual(names(interface_role="API Template Role"), {"Global", "Site"})

    def test_create_with_new_attributes(self):
        self.add_permissions("interface_profiles.add_interfacetemplate")

        response = self.client.post(
            self._get_list_url(),
            {
                "interface_role": self.role.pk,
                "name": "Created",
                "mgmt_only": True,
                "interface_description": "Created by the API",
                "poe_mode": "pse",
                "poe_type": "type3-ieee802.3bt",
                "mode": "q-in-q",
                "qinq_svlan_vid": 1000,
                "set_null_vrf": True,
            },
            format="json",
        )

        self.assertHttpStatus(response, 201)
        self.assertEqual(response.data["interface_description"], "Created by the API")
        self.assertEqual(response.data["poe_type"]["value"], "type3-ieee802.3bt")
        self.assertTrue(response.data["set_null_vrf"])

    def test_rejects_invalid_vids(self):
        self.add_permissions("interface_profiles.add_interfacetemplate")

        with disable_warnings("django.request"):
            response = self.client.post(
                self._get_list_url(),
                {"interface_role": self.role.pk, "name": "Invalid", "tagged_vlans_vids": [5000]},
                format="json",
            )

        self.assertHttpStatus(response, 400)
