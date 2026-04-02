"""
Filtersets for netbox interface profiles.

For more information on NetBox filtersets, see:
https://docs.netbox.dev/en/stable/plugins/development/filtersets/

For django-filters documentation, see:
https://django-filter.readthedocs.io/
"""

from .interface_profile import InterfaceProfileFilterSet

__all__ = ("InterfaceProfileFilterSet",)
