"""
interface profiles

Plugin configuration for interface profiles.

For a complete list of PluginConfig attributes, see:
https://docs.netbox.dev/en/stable/plugins/development/#pluginconfig-attributes
"""

__author__ = """Wouter de Bruijn"""
__email__ = "wouter@retigra.nl"
__version__ = "0.1.0"


from netbox.plugins import PluginConfig


class InterfaceProfilesConfig(PluginConfig):
    name = "interface_profiles"
    verbose_name = "Interface Profiles"
    description = "NetBox plugin for managing interface configuration profiles."
    author = "Wouter de Bruijn"
    author_email = "wouter@retigra.nl"
    version = __version__
    base_url = "interface-profiles"
    min_version = "4.7.0"
    max_version = "4.7.99"
    graphql_schema = "graphql.schema"

    url = "https://github.com/wouterdebruijn/netbox-interface-profiles"

    def ready(self) -> None:
        """Register plugin signal handlers."""
        super().ready()

        # Importing connects Django signal receivers.
        from . import signals  # noqa: F401

    def get_jinja_context(self) -> dict:
        """Expose the interface rendering helpers to config templates."""
        from .jinja_env import context

        return context


config = InterfaceProfilesConfig
