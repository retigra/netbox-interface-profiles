---
description: 'Extensive NetBox Plugin Development Guidelines and Code Conventions'
applyTo: '**/*.py, **/*.html, **/*.toml'
---

# NetBox v4.7 Plugin Development Guidelines

## 1. System Role and Core Objectives
You are an expert Python Django developer and a specialist in **NetBox v4.7 Plugin Development**. Your primary goal is to help build, extend, and maintain NetBox plugins while strictly adhering to the standard NetBox API, coding conventions, and folder structures.

### Constraints & Environment
- **Python Version:** Python 3.12+ (Use modern typing like `list[str]`, `|` for Union, f-strings, and new standard library features).
- **NetBox Version:** v4.7.
- **Frameworks:** Django 5.x, Django REST Framework (DRF), HTMX, and Tailwind CSS (NetBox v4 UI stack).
- **No External Dependencies:** Only use standard Django libraries, NetBox built-ins, and standard Python libraries unless explicitly told otherwise.

## 2. Plugin Folder Structure
A robust NetBox plugin strictly adheres to the following directory structure. Whenever you are asked to create a new component, place it in the corresponding file:

```text
my_plugin/
├── __init__.py           # Contains the PluginConfig subclass
├── models.py             # Database models inheriting from NetBoxModel
├── tables.py             # UI tables inheriting from NetBoxTable
├── forms.py              # Create/Edit, Filter, Bulk Edit, and Import forms
├── filtersets.py         # API and UI filter logic (NetBoxModelFilterSet)
├── views.py              # UI Views (ObjectView, ObjectListView, etc.)
├── urls.py               # UI URL routing
├── navigation.py         # Plugin menu navigation definitions
├── search.py             # Global search index registrations
├── graphql.py            # GraphQL schema mappings
├── api/
│   ├── __init__.py
│   ├── serializers.py    # DRF serializers (NetBoxModelSerializer)
│   ├── views.py          # DRF viewsets (NetBoxModelViewSet)
│   └── urls.py           # API URL routing using NetBoxRouter
├── migrations/           # Django database migrations
└── templates/
    └── my_plugin/
        └── mymodel.html  # Object detail templates extending generic/object.html
```

## 3. The "Full-Stack" Object Creation Guide
When the user asks you to **"add a new Object"** or **"create a new model"** for NetBox, you **MUST** generate the full stack of required components. Do not stop at the model. Follow these exact 12 steps to implement the object completely.

*Assume the model is named `Machine` for the following examples.*

### Step 1: Model (`models.py`)
Inherit from `NetBoxModel`. This automatically adds support for tags, custom fields, comments, and change logging.
```python
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

class Machine(NetBoxModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=30, default='active')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Machine'
        verbose_name_plural = 'Machines'

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse('plugins:my_plugin:machine', args=[self.pk])
```

### Step 2: Table (`tables.py`)
Inherit from `NetBoxTable`. Ensure `actions` is included to provide Edit/Delete buttons in the list view.
```python
import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import Machine

class MachineTable(NetBoxTable):
    name = tables.Column(linkify=True)
    status = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = Machine
        fields = ('pk', 'id', 'name', 'status', 'description', 'actions')
        default_columns = ('name', 'status', 'description')
```

### Step 3: Forms (`forms.py`)
Every object requires four forms: Base, FilterSet, Import, and BulkEdit. Use NetBox form utilities.
```python
from django import forms
from netbox.forms import (
    NetBoxModelForm, NetBoxModelFilterSetForm,
    NetBoxModelImportForm, NetBoxModelBulkEditForm
)
from .models import Machine

class MachineForm(NetBoxModelForm):
    class Meta:
        model = Machine
        fields = ('name', 'status', 'description', 'tags')

class MachineFilterSetForm(NetBoxModelFilterSetForm):
    model = Machine
    name = forms.CharField(required=False)
    status = forms.CharField(required=False)

class MachineImportForm(NetBoxModelImportForm):
    class Meta:
        model = Machine
        fields = ('name', 'status', 'description')

class MachineBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=Machine.objects.all(), widget=forms.MultipleHiddenInput())
    status = forms.CharField(max_length=30, required=False)
    description = forms.CharField(max_length=200, required=False)

    class Meta:
        nullable_fields = ['description']
```

### Step 4: FilterSet (`filtersets.py`)
Provide query string filtering for the list view and API. Must include a `search()` method for the main search bar.
```python
import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from .models import Machine

class MachineFilterSet(NetBoxModelFilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = Machine
        fields = ('id', 'name', 'status', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(name__icontains=value) | queryset.filter(description__icontains=value)
```

### Step 5: UI Views (`views.py`)
Implement the full suite of Generic CRUD Views.
```python
from netbox.views import generic
from . import filtersets, forms, models, tables

class MachineView(generic.ObjectView):
    queryset = models.Machine.objects.all()

class MachineListView(generic.ObjectListView):
    queryset = models.Machine.objects.all()
    table = tables.MachineTable
    filterset = filtersets.MachineFilterSet
    filterset_form = forms.MachineFilterSetForm

class MachineEditView(generic.ObjectEditView):
    queryset = models.Machine.objects.all()
    form = forms.MachineForm

class MachineDeleteView(generic.ObjectDeleteView):
    queryset = models.Machine.objects.all()

class MachineBulkImportView(generic.BulkImportView):
    queryset = models.Machine.objects.all()
    model_form = forms.MachineImportForm
    table = tables.MachineTable

class MachineBulkEditView(generic.BulkEditView):
    queryset = models.Machine.objects.all()
    filterset = filtersets.MachineFilterSet
    table = tables.MachineTable
    form = forms.MachineBulkEditForm

class MachineBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Machine.objects.all()
    filterset = filtersets.MachineFilterSet
    table = tables.MachineTable
```

### Step 6: UI Routing (`urls.py`)
Include all generic endpoints, and standard NetBox auxiliary routes (Changelog and Journal).
```python
from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJournalView
from . import models, views

urlpatterns =[
    path('machines/', views.MachineListView.as_view(), name='machine_list'),
    path('machines/add/', views.MachineEditView.as_view(), name='machine_add'),
    path('machines/import/', views.MachineBulkImportView.as_view(), name='machine_import'),
    path('machines/edit/', views.MachineBulkEditView.as_view(), name='machine_bulk_edit'),
    path('machines/delete/', views.MachineBulkDeleteView.as_view(), name='machine_bulk_delete'),
    path('machines/<int:pk>/', views.MachineView.as_view(), name='machine'),
    path('machines/<int:pk>/edit/', views.MachineEditView.as_view(), name='machine_edit'),
    path('machines/<int:pk>/delete/', views.MachineDeleteView.as_view(), name='machine_delete'),
    path('machines/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='machine_changelog', kwargs={'model': models.Machine}),
    path('machines/<int:pk>/journal/', ObjectJournalView.as_view(), name='machine_journal', kwargs={'model': models.Machine}),
]
```

### Step 7: Object Template (`templates/my_plugin/machine.html`)
Extend `generic/object.html` and utilize standard NetBox v4 inclusion tags for metadata. NetBox v4 relies on HTMX and Tailwind CSS (in place of legacy Bootstrap).
```html
{% extends 'generic/object.html' %}

{% block content %}
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
  <div class="card">
    <div class="card-header">
      <h5 class="card-title">Machine Details</h5>
    </div>
    <div class="card-body">
      <table class="table table-hover attr-table">
        <tr>
          <th scope="row">Name</th>
          <td>{{ object.name }}</td>
        </tr>
        <tr>
          <th scope="row">Status</th>
          <td>{{ object.status }}</td>
        </tr>
        <tr>
          <th scope="row">Description</th>
          <td>{{ object.description|default:"&mdash;" }}</td>
        </tr>
      </table>
    </div>
  </div>

  <div class="space-y-4">
    {% include 'inc/panels/custom_fields.html' %}
    {% include 'inc/panels/tags.html' %}
    {% include 'inc/panels/comments.html' %}
  </div>
</div>
{% endblock %}
```

### Step 8: API Serializer (`api/serializers.py`)
```python
from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import Machine

class MachineSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:my_plugin-api:machine-detail')

    class Meta:
        model = Machine
        fields = (
            'id', 'url', 'display', 'name', 'status', 'description',
            'tags', 'custom_fields', 'created', 'last_updated'
        )
        brief_fields = ('id', 'url', 'display', 'name', 'status')
```

### Step 9: API ViewSet (`api/views.py`)
```python
from netbox.api.viewsets import NetBoxModelViewSet
from .. import filtersets, models
from .serializers import MachineSerializer

class MachineViewSet(NetBoxModelViewSet):
    queryset = models.Machine.objects.all()
    serializer_class = MachineSerializer
    filterset_class = filtersets.MachineFilterSet
```

### Step 10: API Routing (`api/urls.py`)
```python
from netbox.api.routers import NetBoxRouter
from . import views

app_name = 'my_plugin'

router = NetBoxRouter()
router.register('machines', views.MachineViewSet)

urlpatterns = router.urls
```

### Step 11: Navigation Menu (`navigation.py`)
Hook the new object into the left-side navigation.
```python
from netbox.plugins import PluginMenu, PluginMenuItem, PluginMenuButton
from utilities.choices import ButtonColorChoices

machine_buttons =[
    PluginMenuButton(
        link='plugins:my_plugin:machine_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    )
]

menu_items = (
    PluginMenuItem(
        link='plugins:my_plugin:machine_list',
        link_text='Machines',
        buttons=machine_buttons
    ),
)
```

### Step 12: Search Integration (`search.py`)
Ensure the object registers with NetBox's global search engine.
```python
from netbox.search import SearchIndex, register_search
from .models import Machine

@register_search
class MachineIndex(SearchIndex):
    model = Machine
    fields = (
        ('name', 100),
        ('description', 500),
    )
```

### Step 13 (Optional): GraphQL schema (`graphql.py`)
To expose your model via NetBox's GraphQL API.
```python
import graphene
from netbox.graphql.types import NetBoxObjectType
from .models import Machine

class MachineType(NetBoxObjectType):
    class Meta:
        model = Machine
        fields = '__all__'

class Query(graphene.ObjectType):
    machine = graphene.Field(MachineType, id=graphene.Int())
    machine_list = graphene.List(MachineType)

    def resolve_machine(self, info, **kwargs):
        return graphene.Node.get_node_from_global_id(info, kwargs.get('id'), only_type=MachineType)

    def resolve_machine_list(self, info, **kwargs):
        return MachineType._meta.model.objects.restrict(info.context.user, 'view')
```

## 14. Coding Conventions & Best Practices

1. **Python 3.12 syntax**:
   * Heavily use strict type hinting (e.g., `def my_method(self) -> str:`).
   * Utilize the union operator `|` rather than `Optional` or `Union` (e.g., `str | None`).
   * Rely on f-strings for string interpolation.

2. **Database Migrations**:
   * After creating or altering a model, remind the user to generate and apply migrations via the Docker environment. DO NOT attempt to write migration files by hand unless explicitly requested.
   * The plugin can only be validated inside the full NetBox environment provided by the Docker Compose setup in `docker/`. Use `docker compose exec` to run any `manage.py` commands:
     ```bash
     # Generate migrations
     docker compose -f docker/docker-compose.yml exec -it netbox ./manage.py makemigrations netbox_interface_profiles

     # Apply migrations
     docker compose -f docker/docker-compose.yml exec -it netbox ./manage.py migrate

     # Run tests
     docker compose -f docker/docker-compose.yml exec -it netbox ./manage.py test netbox_interface_profiles.tests
     ```
   * DO NOT run any `manage.py` commands directly on the host. All validation, migrations, and tests must go through the Docker environment.

3. **String Constants & Choices**:
   * Use Django's `models.TextChoices` for choice fields, rather than raw tuples. Keep choice definitions cleanly grouped inside or near the model classes.

4. **DRF and API Standards**:
   * Always expose `display` (read-only string representations) and `url` within the serializer fields.
   * Do not forget the `brief_fields` tuple in `Meta`, as NetBox uses this to generate nested representations of objects.

5. **Extending NetBox**:
   * If creating background jobs, use `netbox.jobs` and register them cleanly.
   * If extending existing views with tabs, utilize `utilities.views.register_model_view`.
   * Only use internal undocumented features when absolutely necessary and document the risk explicitly. Always prefer the officially supported NetBox v4.7 Plugin APIs.
```
