"""
Test cases for netbox interface profiles GraphQL API.
"""

from ..models import InterfaceProfile
from ..testing import PluginGraphQLTestCase


class InterfaceProfileGraphQLTestCase(PluginGraphQLTestCase):
    """Test InterfaceProfile GraphQL queries."""

    @classmethod
    def setUpTestData(cls):
        """Create three InterfaceProfile instances."""
        InterfaceProfile.objects.create(name="GraphQL Profile 1", description="First")
        InterfaceProfile.objects.create(name="GraphQL Profile 2", description="Second")
        InterfaceProfile.objects.create(name="GraphQL Profile 3", description="")

    def test_query_single_interface_profile(self):
        """Test querying a single InterfaceProfile by ID."""
        self.add_permissions("netbox_interface_profiles.view_interfaceprofile")

        instance = InterfaceProfile.objects.first()
        query = "query { interface_profile(id: " + str(instance.pk) + ") { id name description } }"

        response = self.execute_query(query)
        self.assertIsNone(response.get("errors"))

        data = response["data"]["interface_profile"]
        self.assertEqual(data["id"], str(instance.pk))
        self.assertEqual(data["name"], instance.name)
        self.assertEqual(data["description"], instance.description)

    def test_query_interface_profile_list(self):
        """Test querying the full list of InterfaceProfile objects."""
        self.add_permissions("netbox_interface_profiles.view_interfaceprofile")

        query = """
        query {
            interface_profile_list {
                id
                name
                description
            }
        }
        """

        response = self.execute_query(query)
        self.assertIsNone(response.get("errors"))

        data = response["data"]["interface_profile_list"]
        self.assertEqual(len(data), 3)
        self.assertIn("id", data[0])
        self.assertIn("name", data[0])
        self.assertIn("description", data[0])

    def test_query_interface_profile_with_timestamps(self):
        """Test querying a record with created and last_updated fields."""
        self.add_permissions("netbox_interface_profiles.view_interfaceprofile")

        instance = InterfaceProfile.objects.first()
        query = "query { interface_profile(id: " + str(instance.pk) + ") { id name created last_updated } }"

        response = self.execute_query(query)
        self.assertIsNone(response.get("errors"))

        data = response["data"]["interface_profile"]
        self.assertEqual(data["id"], str(instance.pk))
        self.assertIsNotNone(data["created"])
        self.assertIsNotNone(data["last_updated"])
