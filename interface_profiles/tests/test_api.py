"""
Test cases for interface profiles REST API.
"""

from dcim.models import Platform
from django.urls import reverse

from ..models import InterfaceRole, ProfileConfigTemplate, RoleGroup
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
