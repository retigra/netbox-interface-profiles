"""
Test cases for netbox interface profiles views.
"""

import re

from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Platform, Site, SiteGroup
from django.test import Client
from django.urls import reverse

from ..models import (
    InterfaceRole,
    InterfaceRoleAssignment,
    InterfaceTemplate,
    ProfileConfigTemplate,
    RoleGroup,
)
from ..tables.interface_role_assignment import DEVICE_INTERFACE_BUTTONS
from ..testing import PluginViewTestCase
from ..testing.utils import disable_warnings, get_random_string


class InterfaceRoleViewTestCase(PluginViewTestCase):
    """Test InterfaceRole list, detail, create, edit, and delete views."""

    @classmethod
    def setUpTestData(cls):
        """Create three InterfaceRole instances."""
        cls.platform = Platform.objects.create(name="View Platform", slug="view-platform")
        InterfaceRole.objects.create(name="View Role 1", description="First")
        InterfaceRole.objects.create(name="View Role 2", description="Second")
        cls.role = InterfaceRole.objects.create(name="View Role 3", description="")
        interface_template = InterfaceTemplate.objects.create(
            interface_role=cls.role,
            name="Related Interface Template",
            enabled=True,
        )
        ProfileConfigTemplate.objects.create(
            interface_template=interface_template,
            platform=cls.platform,
            name="Related Config Template",
            description="",
            template_code="interface {{ interface.name|default('N/A') }}",
        )

    def test_list_interface_roles(self):
        """Test the InterfaceRole list view returns HTTP 200."""
        self.add_permissions("netbox_interface_profiles.view_interfacerole")

        url = reverse("plugins:netbox_interface_profiles:interfacerole_list")
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)

    def test_list_interface_roles_without_permission(self):
        """Test the list view returns HTTP 403 when unauthenticated."""
        url = reverse("plugins:netbox_interface_profiles:interfacerole_list")

        with disable_warnings("django.request"):
            response = self.client.get(url)
            self.assertHttpStatus(response, 403)

    def test_view_interface_role_detail(self):
        """Test the InterfaceRole detail view renders the correct object."""
        self.add_permissions("netbox_interface_profiles.view_interfacerole")
        self.add_permissions(
            "netbox_interface_profiles.view_interfacetemplate",
            "netbox_interface_profiles.view_profileconfigtemplate",
        )

        instance = self.role
        url = reverse("plugins:netbox_interface_profiles:interfacerole", kwargs={"pk": instance.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertEqual(response.context["object"], instance)
        self.assertContains(response, "Related Interface Templates")
        self.assertContains(response, "Related Config Templates")
        self.assertContains(response, reverse("plugins:netbox_interface_profiles:interfacetemplate_list"))
        self.assertContains(response, reverse("plugins:netbox_interface_profiles:profileconfigtemplate_list"))

    def test_interface_role_detail_embedded_tables_list_related_templates(self):
        """The embedded related-template tables only list templates belonging to the role."""
        self.add_permissions(
            "netbox_interface_profiles.view_interfacetemplate",
            "netbox_interface_profiles.view_profileconfigtemplate",
        )
        other_role = InterfaceRole.objects.create(name="Unrelated Role", description="")
        other_template = InterfaceTemplate.objects.create(interface_role=other_role, name="Unrelated Template")
        ProfileConfigTemplate.objects.create(
            interface_template=other_template,
            platform=self.platform,
            name="Unrelated Config Template",
            template_code="",
        )
        params = {"embedded": "True", "interface_role_id": self.role.pk}

        response = self.client.get(reverse("plugins:netbox_interface_profiles:interfacetemplate_list"), params)
        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Related Interface Template")
        self.assertNotContains(response, "Unrelated Template")

        response = self.client.get(reverse("plugins:netbox_interface_profiles:profileconfigtemplate_list"), params)
        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Related Config Template")
        self.assertNotContains(response, "Unrelated Config Template")

    def test_create_interface_role(self):
        """Test creating an InterfaceRole via the add form."""
        self.add_permissions(
            "netbox_interface_profiles.add_interfacerole",
            "netbox_interface_profiles.view_interfacerole",
        )

        url = reverse("plugins:netbox_interface_profiles:interfacerole_add")
        name = f"Created {get_random_string(10)}"
        form_data = self.post_data(
            {
                "name": name,
                "description": "A new role",
            }
        )

        response = self.client.post(url, form_data, follow=True)
        self.assertHttpStatus(response, 200)

        instance = InterfaceRole.objects.get(name=name)
        self.assertEqual(instance.description, "A new role")

    def test_create_interface_role_without_permission(self):
        """Test that the add view returns HTTP 403 without permission."""
        url = reverse("plugins:netbox_interface_profiles:interfacerole_add")

        with disable_warnings("django.request"):
            response = self.client.get(url)
            self.assertHttpStatus(response, 403)

    def test_edit_interface_role(self):
        """Test editing an InterfaceRole name via the edit form."""
        self.add_permissions(
            "netbox_interface_profiles.change_interfacerole",
            "netbox_interface_profiles.view_interfacerole",
        )

        instance = InterfaceRole.objects.first()
        url = reverse("plugins:netbox_interface_profiles:interfacerole_edit", kwargs={"pk": instance.pk})
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

    def test_delete_interface_role(self):
        """Test deleting an InterfaceRole via the delete confirmation view."""
        self.add_permissions(
            "netbox_interface_profiles.delete_interfacerole",
            "netbox_interface_profiles.view_interfacerole",
        )

        instance = InterfaceRole.objects.last()
        pk = instance.pk
        url = reverse("plugins:netbox_interface_profiles:interfacerole_delete", kwargs={"pk": pk})

        response = self.client.post(url, {"confirm": True}, follow=True)
        self.assertHttpStatus(response, 200)
        self.assertFalse(InterfaceRole.objects.filter(pk=pk).exists())

    def test_delete_interface_role_without_permission(self):
        """Test that the delete view returns HTTP 403 without permission."""
        instance = InterfaceRole.objects.first()
        url = reverse("plugins:netbox_interface_profiles:interfacerole_delete", kwargs={"pk": instance.pk})

        with disable_warnings("django.request"):
            response = self.client.get(url)
            self.assertHttpStatus(response, 403)


class InterfaceRoleFormValidationTestCase(PluginViewTestCase):
    """Test InterfaceRole form validation via views."""

    @classmethod
    def setUpTestData(cls):
        """Create an existing entry for validation tests."""
        InterfaceRole.objects.create(name="Existing Role", description="")

    def setUp(self):
        """Grant add and view permissions for the form tests."""
        super().setUp()
        self.add_permissions(
            "netbox_interface_profiles.add_interfacerole",
            "netbox_interface_profiles.view_interfacerole",
        )

    def test_form_rejects_missing_name(self):
        """Test that missing required name re-displays the form (HTTP 200)."""
        url = reverse("plugins:netbox_interface_profiles:interfacerole_add")
        form_data = self.post_data(
            {
                "name": "",
                "description": "Some description",
            }
        )

        response = self.client.post(url, form_data)
        self.assertHttpStatus(response, 200)
        self.assertEqual(InterfaceRole.objects.filter(description="Some description").count(), 0)


class InterfaceRoleInterfacesTabViewTestCase(PluginViewTestCase):
    """Test the Interface Role detail interfaces tab view."""

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name="Interfaces Site", slug="interfaces-site")
        manufacturer = Manufacturer.objects.create(name="Interfaces Manufacturer", slug="interfaces-manufacturer")
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model="Interfaces Device Type",
            slug="interfaces-device-type",
        )
        role = DeviceRole.objects.create(name="Interfaces Device Role", slug="interfaces-device-role")

        cls.device = Device.objects.create(
            name="Interfaces Device",
            site=site,
            device_type=device_type,
            role=role,
        )
        cls.interface = Interface.objects.create(
            device=cls.device,
            name="xe-0/0/0",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        cls.role = InterfaceRole.objects.create(name="Interfaces Tab Role", description="")
        InterfaceRoleAssignment.objects.create(interface=cls.interface, interface_role=cls.role)

    def test_interface_role_interfaces_tab_renders_controls_and_rows(self):
        self.add_permissions(
            "netbox_interface_profiles.view_interfacerole",
            "netbox_interface_profiles.view_interfaceroleassignment",
            "dcim.view_interface",
            "dcim.view_device",
        )

        url = reverse(
            "plugins:netbox_interface_profiles:interfacerole_interfaces",
            kwargs={"pk": self.role.pk},
        )
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Quick search")
        self.assertContains(response, "Saved filter")
        self.assertContains(response, "Configure Table")
        self.assertContains(response, self.interface.name)
        self.assertContains(response, self.device.name)

    def test_interface_role_interfaces_tab_offers_bulk_actions(self):
        self.add_permissions(
            "netbox_interface_profiles.view_interfacerole",
            "netbox_interface_profiles.view_interfaceroleassignment",
            "netbox_interface_profiles.change_interfaceroleassignment",
            "netbox_interface_profiles.delete_interfaceroleassignment",
        )

        url = reverse(
            "plugins:netbox_interface_profiles:interfacerole_interfaces",
            kwargs={"pk": self.role.pk},
        )
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        assignment = InterfaceRoleAssignment.objects.get(interface=self.interface)
        self.assertContains(response, f'name="pk" value="{assignment.pk}"')
        self.assertContains(response, reverse("plugins:netbox_interface_profiles:interfaceroleassignment_bulk_edit"))
        self.assertContains(response, reverse("plugins:netbox_interface_profiles:interfaceroleassignment_bulk_delete"))

    def test_interface_role_interfaces_tab_hides_bulk_actions_without_permission(self):
        self.add_permissions(
            "netbox_interface_profiles.view_interfacerole",
            "netbox_interface_profiles.view_interfaceroleassignment",
        )

        url = reverse(
            "plugins:netbox_interface_profiles:interfacerole_interfaces",
            kwargs={"pk": self.role.pk},
        )
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertNotContains(response, 'name="pk"')
        self.assertNotContains(response, reverse("plugins:netbox_interface_profiles:interfaceroleassignment_bulk_edit"))

    def test_interface_role_interfaces_tab_supports_device_name_search(self):
        self.add_permissions(
            "netbox_interface_profiles.view_interfacerole",
            "netbox_interface_profiles.view_interfaceroleassignment",
            "dcim.view_interface",
            "dcim.view_device",
        )

        url = reverse(
            "plugins:netbox_interface_profiles:interfacerole_interfaces",
            kwargs={"pk": self.role.pk},
        )
        response = self.client.get(url, {"q": self.device.name})

        self.assertHttpStatus(response, 200)
        self.assertContains(response, self.interface.name)
        self.assertContains(response, self.device.name)


class DeviceInterfaceRoleTabViewTestCase(PluginViewTestCase):
    """Test the device interface roles tab view."""

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

        cls.role = InterfaceRole.objects.create(name="Assigned Role", description="")
        InterfaceRoleAssignment.objects.create(interface=cls.interface, interface_role=cls.role)

    def test_device_interface_roles_tab_renders_standard_controls(self):
        self.add_permissions(
            "dcim.view_device",
            "dcim.view_interface",
            "netbox_interface_profiles.view_interfacerole",
            "netbox_interface_profiles.view_interfaceroleassignment",
        )

        url = reverse(
            "dcim:device_interface_roles",
            kwargs={"pk": self.interface.device.pk},
        )
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Quick search")
        self.assertContains(response, "Saved filter")
        self.assertContains(response, "Configure Table")
        self.assertContains(response, "DeviceInterfaceTable_config")
        self.assertContains(response, reverse("dcim:device_interfaces", kwargs={"pk": self.interface.device.pk}))
        self.assertContains(response, "Legacy Interfaces View")
        self.assertContains(response, self.role.get_absolute_url())
        self.assertContains(response, self.role.name)

    def test_device_interface_roles_tab_row_buttons_return_to_tab(self):
        self.add_permissions(
            "dcim.view_device",
            "dcim.view_interface",
            "dcim.change_interface",
            "dcim.add_interface",
            "ipam.add_ipaddress",
            "netbox_interface_profiles.view_interfaceroleassignment",
        )

        device_pk = self.interface.device.pk
        url = reverse("dcim:device_interface_roles", kwargs={"pk": device_pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertContains(response, f"return_url={url}")
        self.assertNotContains(response, f"return_url={reverse('dcim:device_interfaces', kwargs={'pk': device_pk})}")

    def test_legacy_interfaces_tab_renders_banner(self):
        self.add_permissions(
            "dcim.view_device",
            "dcim.view_interface",
            "netbox_interface_profiles.view_interfaceroleassignment",
        )

        device_pk = self.interface.device.pk
        response = self.client.get(reverse("dcim:device_interfaces", kwargs={"pk": device_pk}))

        self.assertHttpStatus(response, 200)
        self.assertContains(response, 'id="legacy-interfaces-banner"')
        self.assertContains(response, reverse("dcim:device_interface_roles", kwargs={"pk": device_pk}))

        response = self.client.get(reverse("dcim:device_interface_roles", kwargs={"pk": device_pk}))
        self.assertNotContains(response, 'id="legacy-interfaces-banner"')

    def test_legacy_interfaces_tab_kept_without_permission(self):
        self.add_permissions("dcim.view_device", "dcim.view_interface")

        response = self.client.get(self.interface.device.get_absolute_url())

        self.assertHttpStatus(response, 200)
        self.assertNotContains(response, "remove_device_interface_tab.js")

    def test_device_interface_buttons_replace_every_legacy_return_url(self):
        # Guards against NetBox changing how INTERFACE_BUTTONS references the legacy tab
        self.assertNotIn("dcim:device_interfaces", DEVICE_INTERFACE_BUTTONS)

    def test_device_interface_roles_tab_offers_bulk_actions(self):
        self.add_permissions(
            "dcim.view_device",
            "dcim.view_interface",
            "dcim.change_interface",
            "dcim.delete_interface",
            "netbox_interface_profiles.view_interfaceroleassignment",
            "netbox_interface_profiles.add_interfaceroleassignment",
            "netbox_interface_profiles.change_interfaceroleassignment",
            "netbox_interface_profiles.delete_interfaceroleassignment",
        )

        url = reverse("dcim:device_interface_roles", kwargs={"pk": self.interface.device.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertContains(response, f'name="pk" value="{self.interface.pk}"')
        self.assertContains(response, reverse("dcim:interface_bulk_edit"))
        self.assertContains(response, reverse("dcim:interface_bulk_rename"))
        self.assertContains(response, reverse("dcim:interface_bulk_disconnect"))
        self.assertContains(response, reverse("dcim:interface_bulk_delete"))
        self.assertContains(response, f'name="_assign" value="{self.role.pk}"')
        self.assertContains(response, 'name="_remove"')

    def test_device_interface_roles_tab_hides_role_actions_without_permission(self):
        self.add_permissions(
            "dcim.view_device",
            "dcim.view_interface",
            "dcim.change_interface",
            "netbox_interface_profiles.view_interfaceroleassignment",
        )

        url = reverse("dcim:device_interface_roles", kwargs={"pk": self.interface.device.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertContains(response, f'name="pk" value="{self.interface.pk}"')
        self.assertNotContains(response, 'name="_assign"')
        self.assertNotContains(response, 'name="_remove"')

    def test_device_interface_roles_tab_bulk_assign(self):
        self.add_permissions(
            "dcim.view_device",
            "dcim.view_interface",
            "netbox_interface_profiles.view_interfaceroleassignment",
            "netbox_interface_profiles.add_interfaceroleassignment",
            "netbox_interface_profiles.change_interfaceroleassignment",
        )
        new_role = InterfaceRole.objects.create(name="Bulk Role", description="")
        other_interface = Interface.objects.get(device=self.interface.device, name="eth1")

        url = reverse("dcim:device_interface_roles", kwargs={"pk": self.interface.device.pk})
        response = self.client.post(url, {"pk": [self.interface.pk, other_interface.pk], "_assign": new_role.pk})

        self.assertHttpStatus(response, 302)
        self.assertEqual(
            InterfaceRoleAssignment.objects.filter(interface_role=new_role).count(),
            2,
        )

    def test_device_interface_roles_tab_bulk_assign_requires_permission(self):
        self.add_permissions(
            "dcim.view_device",
            "dcim.view_interface",
            "netbox_interface_profiles.view_interfaceroleassignment",
        )
        new_role = InterfaceRole.objects.create(name="Bulk Role", description="")

        url = reverse("dcim:device_interface_roles", kwargs={"pk": self.interface.device.pk})
        response = self.client.post(url, {"pk": [self.interface.pk], "_assign": new_role.pk})

        self.assertHttpStatus(response, 403)
        self.assertEqual(InterfaceRoleAssignment.objects.get(interface=self.interface).interface_role, self.role)

    def test_device_interface_roles_tab_bulk_remove(self):
        self.add_permissions(
            "dcim.view_device",
            "dcim.view_interface",
            "netbox_interface_profiles.view_interfaceroleassignment",
            "netbox_interface_profiles.delete_interfaceroleassignment",
        )

        url = reverse("dcim:device_interface_roles", kwargs={"pk": self.interface.device.pk})
        response = self.client.post(url, {"pk": [self.interface.pk], "_remove": ""})

        self.assertHttpStatus(response, 302)
        self.assertFalse(InterfaceRoleAssignment.objects.filter(interface=self.interface).exists())

    def test_device_interface_roles_tab_bulk_remove_requires_permission(self):
        self.add_permissions(
            "dcim.view_device",
            "dcim.view_interface",
            "netbox_interface_profiles.view_interfaceroleassignment",
        )

        url = reverse("dcim:device_interface_roles", kwargs={"pk": self.interface.device.pk})
        response = self.client.post(url, {"pk": [self.interface.pk], "_remove": ""})

        self.assertHttpStatus(response, 403)
        self.assertTrue(InterfaceRoleAssignment.objects.filter(interface=self.interface).exists())

    def test_htmx_menu_endpoint_lists_roles(self):
        self.add_permissions("dcim.view_interface", "netbox_interface_profiles.view_interfaceroleassignment")

        url = reverse(
            "plugins:netbox_interface_profiles:interfaceroleassignment_htmx_menu",
            kwargs={"interface_id": self.interface.pk},
        )
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertContains(response, self.role.name)

    def test_htmx_menu_actions_carry_csrf_token(self):
        """The menu is also rendered outside a form, so its actions must send the CSRF token themselves."""
        self.add_permissions(
            "dcim.view_interface",
            "netbox_interface_profiles.view_interfaceroleassignment",
            "netbox_interface_profiles.change_interfaceroleassignment",
        )
        new_role = InterfaceRole.objects.create(name="CSRF Role", description="")
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)

        response = client.get(
            reverse(
                "plugins:netbox_interface_profiles:interfaceroleassignment_htmx_menu",
                kwargs={"interface_id": self.interface.pk},
            )
        )
        match = re.search(r'hx-headers=\'\{"X-CSRFToken": "([^"]+)"\}\'', response.content.decode())
        self.assertIsNotNone(match)

        url = reverse(
            "plugins:netbox_interface_profiles:interfaceroleassignment_htmx_set",
            kwargs={"interface_id": self.interface.pk, "role_id": new_role.pk},
        )
        response = client.post(url, HTTP_X_CSRFTOKEN=match.group(1))

        self.assertHttpStatus(response, 204)
        self.assertEqual(InterfaceRoleAssignment.objects.get(interface=self.interface).interface_role, new_role)

    def test_htmx_set_endpoint_assigns_role(self):
        # The interface already has an assignment, so this is a change
        self.add_permissions("dcim.view_interface", "netbox_interface_profiles.change_interfaceroleassignment")
        new_role = InterfaceRole.objects.create(name="New HTMX Role", description="")

        url = reverse(
            "plugins:netbox_interface_profiles:interfaceroleassignment_htmx_set",
            kwargs={
                "interface_id": self.interface.pk,
                "role_id": new_role.pk,
            },
        )
        response = self.client.post(url)

        self.assertHttpStatus(response, 204)
        assignment = InterfaceRoleAssignment.objects.get(interface=self.interface)
        self.assertEqual(assignment.interface_role, new_role)

    def test_htmx_remove_endpoint_removes_assignment(self):
        self.add_permissions("netbox_interface_profiles.delete_interfaceroleassignment")

        url = reverse(
            "plugins:netbox_interface_profiles:interfaceroleassignment_htmx_remove",
            kwargs={"interface_id": self.interface.pk},
        )
        response = self.client.post(url)

        self.assertHttpStatus(response, 204)
        self.assertFalse(InterfaceRoleAssignment.objects.filter(interface=self.interface).exists())

    def test_htmx_menu_filters_roles_by_device_role_scope(self):
        """Ensure role-scoped roles are filtered for the device in HTMX menu."""
        self.add_permissions("dcim.view_interface", "netbox_interface_profiles.view_interfaceroleassignment")

        matching_role = InterfaceRole.objects.create(name="Role Matched", description="")
        matching_role.device_roles.add(self.interface.device.role)

        other_role = DeviceRole.objects.create(name="Other Role", slug="other-role")
        non_matching_role = InterfaceRole.objects.create(name="Role Not Matched", description="")
        non_matching_role.device_roles.add(other_role)

        unscoped_role = InterfaceRole.objects.create(name="Role Unscoped", description="")

        url = reverse(
            "plugins:netbox_interface_profiles:interfaceroleassignment_htmx_menu",
            kwargs={"interface_id": self.interface.pk},
        )
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertContains(response, matching_role.name)
        self.assertContains(response, unscoped_role.name)
        self.assertNotContains(response, non_matching_role.name)


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

        cls.role = InterfaceRole.objects.create(name="Interface Detail Role", description="")
        InterfaceRoleAssignment.objects.create(interface=cls.interface, interface_role=cls.role)

        cls.interface_template = InterfaceTemplate.objects.create(
            interface_role=cls.role,
            name="Global Access Template",
            enabled=True,
            speed=1000,
        )
        cls.config_template = ProfileConfigTemplate.objects.create(
            interface_template=cls.interface_template,
            platform=platform,
            device_type=cls.device_type,
            name="Config Detail Template",
            description="",
            template_code="interface {{ interface.name }}\\n description {{ role.name }}",
        )

    def test_interface_detail_card_renders_assignment_templates_and_preview(self):
        self.add_permissions(
            "dcim.view_interface",
            "dcim.view_device",
            "netbox_interface_profiles.view_interfacerole",
            "netbox_interface_profiles.view_interfaceroleassignment",
            "netbox_interface_profiles.view_interfacetemplate",
            "netbox_interface_profiles.view_profileconfigtemplate",
        )

        url = reverse("dcim:interface", kwargs={"pk": self.interface.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Interface Role Automation")
        self.assertContains(response, self.role.name)
        self.assertContains(response, self.interface_template.name)
        self.assertContains(response, self.config_template.name)
        self.assertContains(response, "interface eth0")
        self.assertContains(response, f"description {self.role.name}")

    def test_interface_detail_card_offers_change_for_assigned_interface(self):
        self.add_permissions(
            "dcim.view_interface",
            "netbox_interface_profiles.view_interfaceroleassignment",
            "netbox_interface_profiles.change_interfaceroleassignment",
        )

        response = self.client.get(reverse("dcim:interface", kwargs={"pk": self.interface.pk}))

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Change")
        self.assertContains(
            response,
            reverse(
                "plugins:netbox_interface_profiles:interfaceroleassignment_htmx_menu",
                kwargs={"interface_id": self.interface.pk},
            ),
        )

    def test_interface_detail_card_offers_assign_for_unassigned_interface(self):
        interface = Interface.objects.create(
            device=self.device,
            name="eth1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        self.add_permissions(
            "dcim.view_interface",
            "netbox_interface_profiles.view_interfaceroleassignment",
            "netbox_interface_profiles.add_interfaceroleassignment",
        )

        response = self.client.get(reverse("dcim:interface", kwargs={"pk": interface.pk}))

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "No interface role assigned")
        self.assertContains(
            response,
            reverse(
                "plugins:netbox_interface_profiles:interfaceroleassignment_htmx_menu",
                kwargs={"interface_id": interface.pk},
            ),
        )

    def test_interface_detail_card_hides_assign_without_add_permission(self):
        interface = Interface.objects.create(
            device=self.device,
            name="eth1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        self.add_permissions("dcim.view_interface")

        response = self.client.get(reverse("dcim:interface", kwargs={"pk": interface.pk}))

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "No interface role assigned")
        self.assertNotContains(
            response,
            reverse(
                "plugins:netbox_interface_profiles:interfaceroleassignment_htmx_menu",
                kwargs={"interface_id": interface.pk},
            ),
        )


class InterfaceRoleSyncViewTestCase(PluginViewTestCase):
    """Test queueing role synchronization jobs from InterfaceRole detail."""

    @classmethod
    def setUpTestData(cls):
        cls.role = InterfaceRole.objects.create(name="Sync Role", description="")

    def test_sync_view_requires_change_interface_permission(self):
        url = reverse(
            "plugins:netbox_interface_profiles:interfacerole_sync",
            kwargs={"pk": self.role.pk},
        )
        with disable_warnings("django.request"):
            response = self.client.get(url)
            self.assertHttpStatus(response, 403)

    def test_sync_view_queues_job(self):
        self.add_permissions("dcim.change_interface", "netbox_interface_profiles.view_rolesync")

        url = reverse(
            "plugins:netbox_interface_profiles:interfacerole_sync",
            kwargs={"pk": self.role.pk},
        )
        response = self.client.post(url, {"dry_run": "on"}, follow=False)

        self.assertEqual(response.status_code, 302)


class RoleGroupViewTestCase(PluginViewTestCase):
    """Test RoleGroup list, detail and create views."""

    @classmethod
    def setUpTestData(cls):
        cls.group = RoleGroup.objects.create(name="Access", slug="access", description="Edge ports")
        cls.role = InterfaceRole.objects.create(name="Access VLAN 10", group=cls.group)
        InterfaceRole.objects.create(name="Ungrouped Role")

    def test_list_role_groups(self):
        self.add_permissions("netbox_interface_profiles.view_rolegroup")

        response = self.client.get(reverse("plugins:netbox_interface_profiles:rolegroup_list"))

        self.assertHttpStatus(response, 200)
        self.assertContains(response, self.group.name)

    def test_view_role_group_detail(self):
        self.add_permissions(
            "netbox_interface_profiles.view_rolegroup",
            "netbox_interface_profiles.view_interfacerole",
        )

        response = self.client.get(self.group.get_absolute_url())

        self.assertHttpStatus(response, 200)
        self.assertEqual(response.context["object"], self.group)
        self.assertContains(response, reverse("plugins:netbox_interface_profiles:interfacerole_list"))

    def test_create_role_group(self):
        self.add_permissions("netbox_interface_profiles.add_rolegroup")

        response = self.client.post(
            reverse("plugins:netbox_interface_profiles:rolegroup_add"),
            {"name": "Trunk", "slug": "trunk", "description": "Uplinks"},
        )

        self.assertHttpStatus(response, 302)
        self.assertTrue(RoleGroup.objects.filter(slug="trunk").exists())

    def test_interface_role_list_filters_by_group(self):
        self.add_permissions("netbox_interface_profiles.view_interfacerole")

        url = reverse("plugins:netbox_interface_profiles:interfacerole_list")
        response = self.client.get(url, {"group": self.group.slug})

        self.assertHttpStatus(response, 200)
        self.assertContains(response, self.role.name)
        self.assertNotContains(response, "Ungrouped Role")
