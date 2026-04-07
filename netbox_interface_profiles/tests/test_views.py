"""
Test cases for netbox interface profiles views.
"""

from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Platform, Site, SiteGroup
from django.urls import reverse

from ..models import InterfaceProfile, InterfaceProfileAssignment, InterfaceTemplate, ProfileConfigTemplate
from ..testing import PluginViewTestCase
from ..testing.utils import disable_warnings, get_random_string


class InterfaceProfileViewTestCase(PluginViewTestCase):
    """Test InterfaceProfile list, detail, create, edit, and delete views."""

    @classmethod
    def setUpTestData(cls):
        """Create three InterfaceProfile instances."""
        cls.platform = Platform.objects.create(name="View Platform", slug="view-platform")
        InterfaceProfile.objects.create(name="View Profile 1", description="First")
        InterfaceProfile.objects.create(name="View Profile 2", description="Second")
        cls.profile = InterfaceProfile.objects.create(name="View Profile 3", description="")
        InterfaceTemplate.objects.create(
            interface_profile=cls.profile,
            name="Related Interface Template",
            enabled=True,
        )
        ProfileConfigTemplate.objects.create(
            interface_profile=cls.profile,
            platform=cls.platform,
            name="Related Config Template",
            description="",
            template_code="interface {{ interface.name|default('N/A') }}",
        )

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
        self.add_permissions(
            "netbox_interface_profiles.view_interfacetemplate",
            "netbox_interface_profiles.view_profileconfigtemplate",
        )

        instance = self.profile
        url = reverse("plugins:netbox_interface_profiles:interfaceprofile", kwargs={"pk": instance.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertEqual(response.context["object"], instance)
        self.assertContains(response, "Related Interface Templates")
        self.assertContains(response, "Related Interface Template")
        self.assertContains(response, "Related Config Templates")
        self.assertContains(response, "Related Config Template")

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


class DeviceInterfaceProfileTabViewTestCase(PluginViewTestCase):
    """Test the device interface profiles tab view."""

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name="Site 1", slug="site-1")
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model="Device Type 1",
            slug="device-type-1",
        )
        role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        device = Device.objects.create(name="Device 1", site=site, device_type=device_type, role=role)
        cls.interface = Interface.objects.create(
            device=device,
            name="eth0",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        Interface.objects.create(
            device=device,
            name="eth1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )

        cls.profile = InterfaceProfile.objects.create(name="Assigned Profile", description="")
        InterfaceProfileAssignment.objects.create(interface=cls.interface, interface_profile=cls.profile)

    def test_device_interface_profiles_tab_renders_standard_controls(self):
        self.add_permissions(
            "dcim.view_device",
            "dcim.view_interface",
            "netbox_interface_profiles.view_interfaceprofile",
            "netbox_interface_profiles.view_interfaceprofileassignment",
        )

        url = reverse(
            "dcim:device_interface_profiles",
            kwargs={"pk": self.interface.device.pk},
        )
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Quick search")
        self.assertContains(response, "Saved filter")
        self.assertContains(response, "Configure Table")
        self.assertContains(response, "DeviceInterfaceTable_config")
        self.assertContains(response, self.profile.get_absolute_url())
        self.assertContains(response, self.profile.name)

    def test_htmx_menu_endpoint_lists_profiles(self):
        self.add_permissions("netbox_interface_profiles.view_interfaceprofileassignment")

        url = reverse(
            "plugins:netbox_interface_profiles:interfaceprofileassignment_htmx_menu",
            kwargs={"interface_id": self.interface.pk},
        )
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertContains(response, self.profile.name)

    def test_htmx_set_endpoint_assigns_profile(self):
        self.add_permissions("netbox_interface_profiles.add_interfaceprofileassignment")
        new_profile = InterfaceProfile.objects.create(name="New HTMX Profile", description="")

        url = reverse(
            "plugins:netbox_interface_profiles:interfaceprofileassignment_htmx_set",
            kwargs={
                "interface_id": self.interface.pk,
                "profile_id": new_profile.pk,
            },
        )
        response = self.client.post(url)

        self.assertHttpStatus(response, 204)
        assignment = InterfaceProfileAssignment.objects.get(interface=self.interface)
        self.assertEqual(assignment.interface_profile, new_profile)

    def test_htmx_remove_endpoint_removes_assignment(self):
        self.add_permissions("netbox_interface_profiles.delete_interfaceprofileassignment")

        url = reverse(
            "plugins:netbox_interface_profiles:interfaceprofileassignment_htmx_remove",
            kwargs={"interface_id": self.interface.pk},
        )
        response = self.client.post(url)

        self.assertHttpStatus(response, 204)
        self.assertFalse(InterfaceProfileAssignment.objects.filter(interface=self.interface).exists())

    def test_htmx_menu_filters_profiles_by_device_role_scope(self):
        """Ensure role-scoped profiles are filtered for the device in HTMX menu."""
        self.add_permissions("netbox_interface_profiles.view_interfaceprofileassignment")

        matching_profile = InterfaceProfile.objects.create(name="Role Matched", description="")
        matching_profile.device_roles.add(self.interface.device.device_role)

        other_role = DeviceRole.objects.create(name="Other Role", slug="other-role")
        non_matching_profile = InterfaceProfile.objects.create(name="Role Not Matched", description="")
        non_matching_profile.device_roles.add(other_role)

        unscoped_profile = InterfaceProfile.objects.create(name="Role Unscoped", description="")

        url = reverse(
            "plugins:netbox_interface_profiles:interfaceprofileassignment_htmx_menu",
            kwargs={"interface_id": self.interface.pk},
        )
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertContains(response, matching_profile.name)
        self.assertContains(response, unscoped_profile.name)
        self.assertNotContains(response, non_matching_profile.name)


class InterfaceDetailCardTestCase(PluginViewTestCase):
    """Test the interface detail card rendered by template extension."""

    @classmethod
    def setUpTestData(cls):
        cls.site_group = SiteGroup.objects.create(name="SiteGroup 1", slug="site-group-1")
        cls.site = Site.objects.create(name="Site 2", slug="site-2", group=cls.site_group)
        manufacturer = Manufacturer.objects.create(name="Manufacturer 2", slug="manufacturer-2")
        cls.device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model="Device Type 2",
            slug="device-type-2",
        )
        platform = Platform.objects.create(name="Platform 1", slug="platform-1")
        role = DeviceRole.objects.create(name="Device Role 2", slug="device-role-2")
        cls.device = Device.objects.create(
            name="Device 2",
            site=cls.site,
            device_type=cls.device_type,
            role=role,
            platform=platform,
        )
        cls.interface = Interface.objects.create(
            device=cls.device,
            name="eth0",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )

        cls.profile = InterfaceProfile.objects.create(name="Interface Detail Profile", description="")
        InterfaceProfileAssignment.objects.create(interface=cls.interface, interface_profile=cls.profile)

        cls.interface_template = InterfaceTemplate.objects.create(
            interface_profile=cls.profile,
            name="Global Access Template",
            enabled=True,
            speed=1000,
        )
        cls.config_template = ProfileConfigTemplate.objects.create(
            interface_profile=cls.profile,
            platform=platform,
            device_type=cls.device_type,
            name="Config Detail Template",
            description="",
            template_code="interface {{ interface.name }}\\n description {{ profile.name }}",
        )

    def test_interface_detail_card_renders_assignment_templates_and_preview(self):
        self.add_permissions(
            "dcim.view_interface",
            "dcim.view_device",
            "netbox_interface_profiles.view_interfaceprofile",
            "netbox_interface_profiles.view_interfaceprofileassignment",
            "netbox_interface_profiles.view_interfacetemplate",
            "netbox_interface_profiles.view_profileconfigtemplate",
        )

        url = reverse("dcim:interface", kwargs={"pk": self.interface.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Interface Profile Automation")
        self.assertContains(response, self.profile.name)
        self.assertContains(response, self.interface_template.name)
        self.assertContains(response, self.config_template.name)
        self.assertContains(response, "interface eth0")
        self.assertContains(response, f"description {self.profile.name}")
