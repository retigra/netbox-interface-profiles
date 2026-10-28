"""
API URL patterns for netbox interface profiles.

For more information on NetBox REST API routing, see:
https://docs.netbox.dev/en/stable/plugins/development/rest-api/#routers

For Django REST Framework routers, see:
https://www.django-rest-framework.org/api-guide/routers/
"""

from netbox.api.routers import NetBoxRouter

from .views import (
    InterfaceProfileAssignmentViewSet,
    InterfaceProfileViewSet,
    InterfaceTemplateViewSet,
    ProfileConfigTemplateViewSet,
    ProfileGroupViewSet,
)

app_name = "netbox_interface_profiles"

router = NetBoxRouter()
router.register("profile-groups", ProfileGroupViewSet)
router.register("interface-profiles", InterfaceProfileViewSet)
router.register("interface-profile-assignments", InterfaceProfileAssignmentViewSet)
router.register("interface-templates", InterfaceTemplateViewSet)
router.register("profile-config-templates", ProfileConfigTemplateViewSet)

urlpatterns = router.urls
