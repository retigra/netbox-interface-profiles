"""
Models for netbox interface profiles.

For more information on NetBox models, see:
https://docs.netbox.dev/en/stable/plugins/development/models/

For NetBox model features (tags, custom fields, change logging, etc.), see:
https://docs.netbox.dev/en/stable/development/models/#netbox-model-features
"""

from .interface_profile import InterfaceProfile
from .interface_profile_assignment import InterfaceProfileAssignment
from .profile_config_template import ProfileConfigTemplate

__all__ = (
    "InterfaceProfile",
    "InterfaceProfileAssignment",
    "ProfileConfigTemplate",
)
