"""
RoleGroup forms for netbox interface profiles.
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from netbox.forms import (
    OrganizationalModelBulkEditForm,
    OrganizationalModelFilterSetForm,
    OrganizationalModelForm,
    OrganizationalModelImportForm,
)
from utilities.forms.fields import TagFilterField
from utilities.forms.rendering import FieldSet

from ..models import RoleGroup


class RoleGroupForm(OrganizationalModelForm):
    """Create / Edit form for RoleGroup."""

    fieldsets = (FieldSet("name", "slug", "description", "tags", name=_("Role Group")),)

    class Meta:
        model = RoleGroup
        fields = ("name", "slug", "description", "owner", "comments", "tags")


class RoleGroupImportForm(OrganizationalModelImportForm):
    """CSV import form for RoleGroup."""

    class Meta:
        model = RoleGroup
        fields = ("name", "slug", "description", "owner", "comments", "tags")


class RoleGroupBulkEditForm(OrganizationalModelBulkEditForm):
    """Bulk edit form for RoleGroup."""

    model = RoleGroup

    pk = forms.ModelMultipleChoiceField(
        queryset=RoleGroup.objects.all(),
        widget=forms.MultipleHiddenInput(),
    )

    fieldsets = (FieldSet("description"),)
    nullable_fields = ("description", "comments")


class RoleGroupFilterSetForm(OrganizationalModelFilterSetForm):
    """Filter form for the RoleGroup list view."""

    model = RoleGroup
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("owner_group_id", "owner_id", name=_("Ownership")),
    )
    tag = TagFilterField(model)
