"""
API viewsets for interface profiles.

For more information on NetBox REST API viewsets, see:
https://docs.netbox.dev/en/stable/plugins/development/rest-api/#viewsets

For Django REST Framework viewsets, see:
https://www.django-rest-framework.org/api-guide/viewsets/
"""

from .interface_config import InterfaceConfigViewSet
from .interface_role import InterfaceRoleViewSet
from .interface_role_assignment import InterfaceRoleAssignmentViewSet
from .interface_template import InterfaceTemplateViewSet
from .profile_config_template import ProfileConfigTemplateViewSet
from .role_group import RoleGroupViewSet

__all__ = (
    "InterfaceConfigViewSet",
    "InterfaceRoleAssignmentViewSet",
    "InterfaceRoleViewSet",
    "InterfaceTemplateViewSet",
    "ProfileConfigTemplateViewSet",
    "RoleGroupViewSet",
)
