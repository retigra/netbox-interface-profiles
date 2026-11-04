"""
API URL patterns for interface profiles.

For more information on NetBox REST API routing, see:
https://docs.netbox.dev/en/stable/plugins/development/rest-api/#routers

For Django REST Framework routers, see:
https://www.django-rest-framework.org/api-guide/routers/
"""

from netbox.api.routers import NetBoxRouter

from .views import (
    InterfaceRoleAssignmentViewSet,
    InterfaceRoleViewSet,
    InterfaceTemplateViewSet,
    ProfileConfigTemplateViewSet,
    RoleGroupViewSet,
)

app_name = "interface_profiles"

router = NetBoxRouter()
router.register("role-groups", RoleGroupViewSet)
router.register("interface-roles", InterfaceRoleViewSet)
router.register("interface-role-assignments", InterfaceRoleAssignmentViewSet)
router.register("interface-templates", InterfaceTemplateViewSet)
router.register("profile-config-templates", ProfileConfigTemplateViewSet)

urlpatterns = router.urls
