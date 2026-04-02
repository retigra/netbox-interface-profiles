"""
Test cases for netbox interface profiles REST API.
"""

from ..models import InterfaceProfile
from ..testing import PluginAPITestCase
from ..testing.utils import disable_warnings, get_random_string


class InterfaceProfileAPITestCase(PluginAPITestCase):
    """Test InterfaceProfile API endpoints."""

    @classmethod
    def setUpTestData(cls):
        """Create three InterfaceProfile instances."""
        InterfaceProfile.objects.create(name="API Profile 1", description="First")
        InterfaceProfile.objects.create(name="API Profile 2", description="Second")
        InterfaceProfile.objects.create(name="API Profile 3", description="")

    def setUp(self):
        """Set up URL names for InterfaceProfile endpoints."""
        super().setUp()
        self.list_url_name = "plugins-api:netbox_interface_profiles-api:interfaceprofile-list"
        self.detail_url_name = "plugins-api:netbox_interface_profiles-api:interfaceprofile-detail"

    def test_list_interface_profiles(self):
        """Test GET request returns all InterfaceProfile objects."""
        self.add_permissions("netbox_interface_profiles.view_interfaceprofile")

        url = self._get_list_url()
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertEqual(response.data["count"], 3)
        self.assertIn("results", response.data)

    def test_list_interface_profiles_without_permission(self):
        """Test GET request without permission returns 403."""
        url = self._get_list_url()

        with disable_warnings("django.request"):
            response = self.client.get(url)
            self.assertHttpStatus(response, 403)

    def test_get_interface_profile(self):
        """Test GET request for a single InterfaceProfile."""
        self.add_permissions("netbox_interface_profiles.view_interfaceprofile")

        instance = InterfaceProfile.objects.first()
        url = self._get_detail_url(instance)
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertEqual(response.data["id"], instance.pk)
        self.assertEqual(response.data["name"], instance.name)

    def test_create_interface_profile(self):
        """Test POST request creates an InterfaceProfile."""
        self.add_permissions("netbox_interface_profiles.add_interfaceprofile")

        url = self._get_list_url()
        name = f"API Created {get_random_string(10)}"
        data = {
            "name": name,
            "description": "Created via API",
        }

        response = self.client.post(url, data, format="json")
        self.assertHttpStatus(response, 201)

        instance = InterfaceProfile.objects.get(name=name)
        self.assertEqual(instance.description, "Created via API")
        self.assertEqual(response.data["id"], instance.pk)

    def test_create_interface_profile_with_blank_description(self):
        """Test POST request accepts a blank optional description."""
        self.add_permissions("netbox_interface_profiles.add_interfaceprofile")

        url = self._get_list_url()
        data = {
            "name": f"No Desc {get_random_string(6)}",
            "description": "",
        }

        response = self.client.post(url, data, format="json")
        self.assertHttpStatus(response, 201)
        self.assertEqual(response.data["description"], "")

    def test_create_interface_profile_without_permission(self):
        """Test POST request without permission returns 403."""
        url = self._get_list_url()

        with disable_warnings("django.request"):
            response = self.client.post(
                url,
                {"name": "Test", "description": ""},
                format="json",
            )
            self.assertHttpStatus(response, 403)

    def test_update_interface_profile(self):
        """Test PATCH request updates an InterfaceProfile name."""
        self.add_permissions("netbox_interface_profiles.change_interfaceprofile")

        instance = InterfaceProfile.objects.first()
        url = self._get_detail_url(instance)
        new_name = f"Updated {get_random_string(10)}"

        response = self.client.patch(url, {"name": new_name}, format="json")
        self.assertHttpStatus(response, 200)

        instance.refresh_from_db()
        self.assertEqual(instance.name, new_name)

    def test_update_interface_profile_without_permission(self):
        """Test PATCH request without permission returns 403."""
        instance = InterfaceProfile.objects.first()
        url = self._get_detail_url(instance)

        with disable_warnings("django.request"):
            response = self.client.patch(url, {"name": "Test"}, format="json")
            self.assertHttpStatus(response, 403)

    def test_delete_interface_profile(self):
        """Test DELETE request removes an InterfaceProfile."""
        self.add_permissions("netbox_interface_profiles.delete_interfaceprofile")

        instance = InterfaceProfile.objects.last()
        pk = instance.pk
        url = self._get_detail_url(instance)

        response = self.client.delete(url)
        self.assertHttpStatus(response, 204)
        self.assertFalse(InterfaceProfile.objects.filter(pk=pk).exists())

    def test_delete_interface_profile_without_permission(self):
        """Test DELETE request without permission returns 403."""
        instance = InterfaceProfile.objects.first()
        url = self._get_detail_url(instance)

        with disable_warnings("django.request"):
            response = self.client.delete(url)
            self.assertHttpStatus(response, 403)

    def test_options_endpoint(self):
        """Test OPTIONS request on the list endpoint succeeds."""
        self.add_permissions("netbox_interface_profiles.view_interfaceprofile")

        url = self._get_list_url()
        response = self.client.options(url)
        self.assertHttpStatus(response, 200)


class InterfaceProfileAPIValidationTestCase(PluginAPITestCase):
    """Test InterfaceProfile API input validation."""

    def setUp(self):
        """Grant add permission and set URL name."""
        super().setUp()
        self.add_permissions("netbox_interface_profiles.add_interfaceprofile")
        self.list_url_name = "plugins-api:netbox_interface_profiles-api:interfaceprofile-list"

    def test_create_with_missing_name(self):
        """Test that missing name is rejected with HTTP 400."""
        url = self._get_list_url()
        data = {"name": "", "description": "Some description"}

        response = self.client.post(url, data, format="json")
        self.assertHttpStatus(response, 400)
        self.assertIn("name", response.data)
