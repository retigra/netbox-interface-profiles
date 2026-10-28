"""
Test cases for netbox interface profiles GraphQL API.
"""

from dcim.models import Platform

from ..models import InterfaceRole, InterfaceTemplate, ProfileConfigTemplate
from ..testing import PluginGraphQLTestCase
from ..testing.utils import create_tags


class InterfaceRoleGraphQLTestCase(PluginGraphQLTestCase):
    """Test InterfaceRole GraphQL queries."""

    @classmethod
    def setUpTestData(cls):
        """Create three InterfaceRole instances."""
        InterfaceRole.objects.create(name="GraphQL Role 1", description="First")
        InterfaceRole.objects.create(name="GraphQL Role 2", description="Second")
        InterfaceRole.objects.create(name="GraphQL Role 3", description="")

    def test_query_single_interface_role(self):
        """Test querying a single InterfaceRole by ID."""
        self.add_permissions("netbox_interface_profiles.view_interfacerole")

        instance = InterfaceRole.objects.first()
        query = "query { interface_role(id: " + str(instance.pk) + ") { id name description } }"

        response = self.execute_query(query)
        self.assertIsNone(response.get("errors"))

        data = response["data"]["interface_role"]
        self.assertEqual(data["id"], str(instance.pk))
        self.assertEqual(data["name"], instance.name)
        self.assertEqual(data["description"], instance.description)

    def test_query_interface_role_list(self):
        """Test querying the full list of InterfaceRole objects."""
        self.add_permissions("netbox_interface_profiles.view_interfacerole")

        query = """
        query {
            interface_role_list {
                id
                name
                description
            }
        }
        """

        response = self.execute_query(query)
        self.assertIsNone(response.get("errors"))

        data = response["data"]["interface_role_list"]
        self.assertEqual(len(data), 3)
        self.assertIn("id", data[0])
        self.assertIn("name", data[0])
        self.assertIn("description", data[0])

    def test_query_interface_role_with_timestamps(self):
        """Test querying a record with created and last_updated fields."""
        self.add_permissions("netbox_interface_profiles.view_interfacerole")

        instance = InterfaceRole.objects.first()
        query = "query { interface_role(id: " + str(instance.pk) + ") { id name created last_updated } }"

        response = self.execute_query(query)
        self.assertIsNone(response.get("errors"))

        data = response["data"]["interface_role"]
        self.assertEqual(data["id"], str(instance.pk))
        self.assertIsNotNone(data["created"])
        self.assertIsNotNone(data["last_updated"])


class InterfaceRoleTemplateGraphQLTestCase(PluginGraphQLTestCase):
    """Test InterfaceTemplate GraphQL queries (exposed as interface_role_template)."""

    @classmethod
    def setUpTestData(cls):
        cls.role = InterfaceRole.objects.create(name="GraphQL Template Role", description="")
        cls.template = InterfaceTemplate.objects.create(
            interface_role=cls.role,
            name="GraphQL Template",
            mtu=9000,
            mode="access",
        )

    def test_query_interface_role_template_with_relations(self):
        """Test the plugin template type exposes its own fields and does not collide with dcim's."""
        self.add_permissions(
            "netbox_interface_profiles.view_interfacerole",
            "netbox_interface_profiles.view_interfacetemplate",
        )

        query = """
        query {
            interface_role_template_list {
                id
                name
                mtu
                mode
                interface_role { id name }
            }
        }
        """

        response = self.execute_query(query)
        self.assertIsNone(response.get("errors"))

        data = response["data"]["interface_role_template_list"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], self.template.name)
        self.assertEqual(data[0]["mtu"], 9000)
        self.assertEqual(data[0]["mode"], "access")
        self.assertEqual(data[0]["interface_role"]["id"], str(self.role.pk))


class ProfileConfigTemplateGraphQLTestCase(PluginGraphQLTestCase):
    """Test ProfileConfigTemplate GraphQL queries."""

    @classmethod
    def setUpTestData(cls):
        cls.role = InterfaceRole.objects.create(name="GraphQL Config Role")
        platform = Platform.objects.create(name="GraphQL Platform", slug="graphql-platform")
        cls.template = ProfileConfigTemplate.objects.create(
            name="GraphQL Config Template", interface_role=cls.role, platform=platform, weight=42, template_code="!"
        )
        cls.template.device_tags.set(create_tags(["GraphQL Device Tag"]))

    def test_query_profile_config_template_list(self):
        self.add_permissions(
            "netbox_interface_profiles.view_interfacerole",
            "netbox_interface_profiles.view_profileconfigtemplate",
            "dcim.view_platform",
            "extras.view_tag",
        )

        query = """
        query {
            profile_config_template_list {
                name
                weight
                interface_role { id }
                platform { slug }
                device_tags { slug }
                interface_tags { slug }
                data_file { id }
            }
        }
        """

        response = self.execute_query(query)
        self.assertIsNone(response.get("errors"))

        data = response["data"]["profile_config_template_list"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["weight"], 42)
        self.assertEqual(data[0]["interface_role"]["id"], str(self.role.pk))
        self.assertEqual(data[0]["device_tags"], [{"slug": "graphql-device-tag"}])
        self.assertEqual(data[0]["interface_tags"], [])
        self.assertIsNone(data[0]["data_file"])
