"""
Test cases for netbox interface profiles views.
"""

from django.urls import reverse

from ..models import InterfaceProfile
from ..testing import PluginViewTestCase
from ..testing.utils import disable_warnings, get_random_string


class InterfaceProfileViewTestCase(PluginViewTestCase):
    """Test InterfaceProfile list, detail, create, edit, and delete views."""

    @classmethod
    def setUpTestData(cls):
        """Create three InterfaceProfile instances."""
        InterfaceProfile.objects.create(name="View Profile 1", description="First")
        InterfaceProfile.objects.create(name="View Profile 2", description="Second")
        InterfaceProfile.objects.create(name="View Profile 3", description="")

    def test_list_interface_profiles(self):
        """Test the InterfaceProfile list view returns HTTP 200."""
        self.add_permissions("netbox_interface_profiles.view_interfaceprofile")

        url = reverse("plugins:netbox_interface_profiles:interfaceprofile_list")
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)

    def test_list_interface_profiles_without_permission(self):
        """Test the list view returns HTTP 403 when unauthenticated."""
        url = reverse("plugins:netbox_interface_profiles:interfaceprofile_list")

        with disable_warnings("django.request"):
            response = self.client.get(url)
            self.assertHttpStatus(response, 403)

    def test_view_interface_profile_detail(self):
        """Test the InterfaceProfile detail view renders the correct object."""
        self.add_permissions("netbox_interface_profiles.view_interfaceprofile")

        instance = InterfaceProfile.objects.first()
        url = reverse("plugins:netbox_interface_profiles:interfaceprofile", kwargs={"pk": instance.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertEqual(response.context["object"], instance)

    def test_create_interface_profile(self):
        """Test creating an InterfaceProfile via the add form."""
        self.add_permissions(
            "netbox_interface_profiles.add_interfaceprofile",
            "netbox_interface_profiles.view_interfaceprofile",
        )

        url = reverse("plugins:netbox_interface_profiles:interfaceprofile_add")
        name = f"Created {get_random_string(10)}"
        form_data = self.post_data(
            {
                "name": name,
                "description": "A new profile",
            }
        )

        response = self.client.post(url, form_data, follow=True)
        self.assertHttpStatus(response, 200)

        instance = InterfaceProfile.objects.get(name=name)
        self.assertEqual(instance.description, "A new profile")

    def test_create_interface_profile_without_permission(self):
        """Test that the add view returns HTTP 403 without permission."""
        url = reverse("plugins:netbox_interface_profiles:interfaceprofile_add")

        with disable_warnings("django.request"):
            response = self.client.get(url)
            self.assertHttpStatus(response, 403)

    def test_edit_interface_profile(self):
        """Test editing an InterfaceProfile name via the edit form."""
        self.add_permissions(
            "netbox_interface_profiles.change_interfaceprofile",
            "netbox_interface_profiles.view_interfaceprofile",
        )

        instance = InterfaceProfile.objects.first()
        url = reverse("plugins:netbox_interface_profiles:interfaceprofile_edit", kwargs={"pk": instance.pk})
        new_name = f"Edited {get_random_string(10)}"
        form_data = self.post_data(
            {
                "name": new_name,
                "description": instance.description,
            }
        )

        response = self.client.post(url, form_data, follow=True)
        self.assertHttpStatus(response, 200)

        instance.refresh_from_db()
        self.assertEqual(instance.name, new_name)

    def test_delete_interface_profile(self):
        """Test deleting an InterfaceProfile via the delete confirmation view."""
        self.add_permissions(
            "netbox_interface_profiles.delete_interfaceprofile",
            "netbox_interface_profiles.view_interfaceprofile",
        )

        instance = InterfaceProfile.objects.last()
        pk = instance.pk
        url = reverse("plugins:netbox_interface_profiles:interfaceprofile_delete", kwargs={"pk": pk})

        response = self.client.post(url, {"confirm": True}, follow=True)
        self.assertHttpStatus(response, 200)
        self.assertFalse(InterfaceProfile.objects.filter(pk=pk).exists())

    def test_delete_interface_profile_without_permission(self):
        """Test that the delete view returns HTTP 403 without permission."""
        instance = InterfaceProfile.objects.first()
        url = reverse("plugins:netbox_interface_profiles:interfaceprofile_delete", kwargs={"pk": instance.pk})

        with disable_warnings("django.request"):
            response = self.client.get(url)
            self.assertHttpStatus(response, 403)


class InterfaceProfileFormValidationTestCase(PluginViewTestCase):
    """Test InterfaceProfile form validation via views."""

    @classmethod
    def setUpTestData(cls):
        """Create an existing entry for validation tests."""
        InterfaceProfile.objects.create(name="Existing Profile", description="")

    def setUp(self):
        """Grant add and view permissions for the form tests."""
        super().setUp()
        self.add_permissions(
            "netbox_interface_profiles.add_interfaceprofile",
            "netbox_interface_profiles.view_interfaceprofile",
        )

    def test_form_rejects_missing_name(self):
        """Test that missing required name re-displays the form (HTTP 200)."""
        url = reverse("plugins:netbox_interface_profiles:interfaceprofile_add")
        form_data = self.post_data(
            {
                "name": "",
                "description": "Some description",
            }
        )

        response = self.client.post(url, form_data)
        self.assertHttpStatus(response, 200)
        self.assertEqual(InterfaceProfile.objects.filter(description="Some description").count(), 0)
