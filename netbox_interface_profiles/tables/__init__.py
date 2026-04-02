"""
Tables for netbox interface profiles.

For more information on NetBox tables, see:
https://docs.netbox.dev/en/stable/plugins/development/tables/

For django-tables2 documentation, see:
https://django-tables2.readthedocs.io/
"""

from .interface_profile import InterfaceProfileTable
from .profile_config_template import ProfileConfigTemplateTable

__all__ = (
    "InterfaceProfileTable",
    "ProfileConfigTemplateTable",
)
