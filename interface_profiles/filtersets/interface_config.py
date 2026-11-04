"""
Filterset for the interface configuration API endpoint.
"""

import django_filters
from dcim.filtersets import InterfaceFilterSet
from dcim.models import Interface

from ..models import InterfaceRole, RoleGroup


class InterfaceConfigFilterSet(InterfaceFilterSet):
    """All filters of NetBox's interface endpoint, plus filters on the assigned interface role."""

    interface_role_id = django_filters.ModelMultipleChoiceFilter(
        field_name="role_assignment__interface_role",
        queryset=InterfaceRole.objects.all(),
        label="Interface Role (ID)",
    )
    interface_role = django_filters.ModelMultipleChoiceFilter(
        field_name="role_assignment__interface_role__name",
        queryset=InterfaceRole.objects.all(),
        to_field_name="name",
        label="Interface Role (name)",
    )
    interface_role_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name="role_assignment__interface_role__group",
        queryset=RoleGroup.objects.all(),
        label="Role Group (ID)",
    )
    interface_role_group = django_filters.ModelMultipleChoiceFilter(
        field_name="role_assignment__interface_role__group__slug",
        queryset=RoleGroup.objects.all(),
        to_field_name="slug",
        label="Role Group (slug)",
    )
    has_interface_role = django_filters.BooleanFilter(
        field_name="role_assignment",
        lookup_expr="isnull",
        exclude=True,
        label="Has an interface role",
    )

    class Meta(InterfaceFilterSet.Meta):
        model = Interface
