"""
API serializers for interface profiles.

Serializers are required for NetBox event handling (webhooks, change logging).
They also power the REST API endpoints.

For more information on NetBox REST API serializers, see:
https://docs.netbox.dev/en/stable/plugins/development/rest-api/#serializers

For Django REST Framework serializers, see:
https://www.django-rest-framework.org/api-guide/serializers/
"""

from .interface_role import InterfaceRoleSerializer
from .interface_role_assignment import InterfaceRoleAssignmentSerializer
from .interface_template import InterfaceTemplateSerializer
from .profile_config_template import ProfileConfigTemplateSerializer
from .role_group import RoleGroupSerializer

__all__ = (
    "InterfaceRoleAssignmentSerializer",
    "InterfaceRoleSerializer",
    "InterfaceTemplateSerializer",
    "ProfileConfigTemplateSerializer",
    "RoleGroupSerializer",
)
