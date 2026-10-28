"""
ProfileGroup forms for netbox interface profiles.
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

from ..models import ProfileGroup


class ProfileGroupForm(OrganizationalModelForm):
    """Create / Edit form for ProfileGroup."""

    fieldsets = (FieldSet("name", "slug", "description", "tags", name=_("Profile Group")),)

    class Meta:
        model = ProfileGroup
        fields = ("name", "slug", "description", "owner", "comments", "tags")


class ProfileGroupImportForm(OrganizationalModelImportForm):
    """CSV import form for ProfileGroup."""

    class Meta:
        model = ProfileGroup
        fields = ("name", "slug", "description", "owner", "comments", "tags")


class ProfileGroupBulkEditForm(OrganizationalModelBulkEditForm):
    """Bulk edit form for ProfileGroup."""

    model = ProfileGroup

    pk = forms.ModelMultipleChoiceField(
        queryset=ProfileGroup.objects.all(),
        widget=forms.MultipleHiddenInput(),
    )

    fieldsets = (FieldSet("description"),)
    nullable_fields = ("description", "comments")


class ProfileGroupFilterSetForm(OrganizationalModelFilterSetForm):
    """Filter form for the ProfileGroup list view."""

    model = ProfileGroup
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("owner_group_id", "owner_id", name=_("Ownership")),
    )
    tag = TagFilterField(model)
