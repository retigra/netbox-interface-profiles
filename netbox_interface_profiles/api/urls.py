"""
API URL patterns for netbox interface profiles.

For more information on NetBox REST API routing, see:
https://docs.netbox.dev/en/stable/plugins/development/rest-api/#routers

For Django REST Framework routers, see:
https://www.django-rest-framework.org/api-guide/routers/
"""

from netbox.api.routers import NetBoxRouter

from .views import InterfaceProfileViewSet

app_name = "netbox_interface_profiles"

router = NetBoxRouter()
router.register("interface-profiles", InterfaceProfileViewSet)

urlpatterns = router.urls
