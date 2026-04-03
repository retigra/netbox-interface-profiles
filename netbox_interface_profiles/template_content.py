"""
Template extensions for netbox interface profiles.
"""

from netbox.plugins import PluginTemplateExtension


class DeviceHeadScripts(PluginTemplateExtension):
    """Inject plugin JS into the <head> of every Device object page.

    Scoping to 'dcim.device' means head() is called on the Device detail view
    and all tabs registered via register_model_view (including our own
    DeviceInterfaceProfileTabView), but not on the Device list view.
    """

    def head(self) -> str:
        return self.render("netbox_interface_profiles/remove_device_interface_tab.html")


template_extensions = [DeviceHeadScripts]
