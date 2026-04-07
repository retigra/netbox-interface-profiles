"""
API viewsets for netbox interface profiles.

For more information on NetBox REST API viewsets, see:
https://docs.netbox.dev/en/stable/plugins/development/rest-api/#viewsets

For Django REST Framework viewsets, see:
https://www.django-rest-framework.org/api-guide/viewsets/
"""

from .interface_profile import InterfaceProfileViewSet
from .interface_profile_assignment import InterfaceProfileAssignmentViewSet
from .interface_template import InterfaceTemplateViewSet
from .profile_config_template import ProfileConfigTemplateViewSet

__all__ = (
    "InterfaceProfileAssignmentViewSet",
    "InterfaceProfileViewSet",
    "InterfaceTemplateViewSet",
    "ProfileConfigTemplateViewSet",
)
