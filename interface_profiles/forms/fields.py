"""
Form fields for interface profiles.
"""

from django import forms
from django.contrib.contenttypes.models import ContentType
from utilities.forms.fields import ContentTypeChoiceField, DynamicModelMultipleChoiceField, GenericObjectChoiceField
from utilities.forms.widgets import APISelectMultiple, GenericObjectSelect, HTMXSelect

__all__ = ("GenericObjectMultipleChoiceField",)


class GenericObjectMultipleSelect(GenericObjectSelect):
    """GenericObjectSelect with a multiple object selector."""

    template_name = "interface_profiles/widgets/generic_object_multiple.html"


class GenericObjectMultipleChoiceField(GenericObjectChoiceField):
    """
    Select one or more objects of a single object type.

    The multiple choice version of NetBox's GenericObjectChoiceField, rendered as a content type selector plus an
    API-backed multiple object selector. The rendered inputs are named "<field>_content_type" and
    "<field>_object_id". The cleaned value is a queryset of the selected objects, or None when no object type is
    selected.
    """

    def __init__(
        self,
        *,
        content_type_queryset,
        query_params=None,
        selector=False,
        hx_method="get",
        hx_include_id="form_fields",
        hx_target_id=None,
        **kwargs,
    ):
        # Mirrors GenericObjectChoiceField.__init__(), with a multiple object field and widget
        self.content_type_queryset = content_type_queryset
        self._content_type_cache = {}
        self.query_params = query_params or {}
        self.selector = selector
        self.gfk_name = None
        self.hx_target_id = hx_target_id
        self.selected_model = None

        htmx_attrs = {}
        if hx_target_id is None and hx_method.lower() == "post":
            htmx_attrs["hx-select"] = "#form_fields"
        content_type_widget = HTMXSelect(
            method=hx_method,
            hx_include_id=hx_include_id,
            hx_target_id=hx_target_id,
            attrs=htmx_attrs or None,
        )
        object_widget = APISelectMultiple()

        fields = (
            ContentTypeChoiceField(queryset=content_type_queryset, required=False, widget=content_type_widget),
            DynamicModelMultipleChoiceField(
                queryset=ContentType.objects.none(), required=False, selector=selector, widget=object_widget
            ),
        )
        widget = GenericObjectMultipleSelect(content_type_widget=content_type_widget, object_widget=object_widget)

        forms.MultiValueField.__init__(self, fields=fields, require_all_fields=False, widget=widget, **kwargs)

    @staticmethod
    def _as_list(value) -> list:
        if value in (None, ""):
            return []
        if isinstance(value, (list, tuple)):
            return [v for v in value if v not in (None, "")]
        return [value]

    def _resolve_subvalue(self, form, field_name, suffix):
        # Bound data holds the object IDs as a list, initial data as a list or a single value
        key = f"{field_name}_{suffix}"
        if suffix == "object_id":
            if form.is_bound and key in form.data:
                return form.data.getlist(key) if hasattr(form.data, "getlist") else self._as_list(form.data[key])
            if key in form.initial:
                return self._as_list(form.initial[key])
            return []
        return super()._resolve_subvalue(form, field_name, suffix)

    def _configure_object_field(self, content_type, object_value=None):
        model = content_type.model_class() if content_type else None
        # Keep a queryset already restricted by restrict_form_fields(), before it is narrowed below
        queryset = self._get_object_queryset(model) if model else None

        model = super()._configure_object_field(content_type, None)
        if model is not None and (object_ids := self._as_list(object_value)):
            try:
                self._set_object_queryset(queryset.filter(pk__in=object_ids))
            except (TypeError, ValueError):
                pass
        return model
