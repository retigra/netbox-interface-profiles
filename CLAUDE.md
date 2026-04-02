# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`netbox-interface-profiles` is a NetBox 4.5 plugin (Django app) for managing interface configuration profiles. It targets NetBox 4.5.x (`min_version = "4.5.0"`, `max_version = "4.5.99"`), Python 3.12+, Django 5.x, Django REST Framework, HTMX, and Tailwind CSS. No external dependencies beyond NetBox's own stack are allowed.

## Commands

All linting/formatting targets operate on `netbox_interface_profiles/` and `tests/`.

```bash
make format      # auto-fix imports (isort) and format with ruff
make lint        # ruff check (no auto-fix)
make test        # format + lint + unittest
make pre-commit  # run all pre-commit hooks across the repo
```

Ruff is configured at line-length 120, target Python 3.12 (`pyproject.toml`).

### Running tests

Tests require a running NetBox installation with PostgreSQL and Redis. The recommended approach is via Docker Compose (see `docker/`):

```bash
# Run all plugin tests
docker compose -f docker/docker-compose.yml exec -it netbox ./manage.py test netbox_interface_profiles.tests

# Run a specific test module
docker compose -f docker/docker-compose.yml exec -it netbox ./manage.py test netbox_interface_profiles.tests.test_models

# Run a specific test class or method
docker compose -f docker/docker-compose.yml exec -it netbox ./manage.py test netbox_interface_profiles.tests.test_models.InterfaceProfileTestCase.test_create
```

Flags used in CI: `--parallel --keepdb -v 2`.

### Migrations

Never write migration files by hand. After changing models, instruct the user to run:

```bash
docker compose -f docker/docker-compose.yml exec -it netbox ./manage.py makemigrations netbox_interface_profiles
docker compose -f docker/docker-compose.yml exec -it netbox ./manage.py migrate
```

Migrations are applied automatically on container startup. CI checks for missing migrations via `makemigrations --check`.

### Type checking

```bash
uv run ty check netbox_interface_profiles/
```

`netbox-types` (dev dependency) provides NetBox stubs. The `netbox_interface_profiles/testing/` directory is excluded from type checking.

## Architecture

### Plugin module layout

Each component is a sub-package with per-model files rather than a flat file:

```
netbox_interface_profiles/
├── __init__.py              # PluginConfig (NetBoxInterfaceProfilesConfig)
├── models/interface_profile.py
├── tables/interface_profile.py
├── forms/interface_profile.py
├── filtersets/interface_profile.py
├── views/interface_profile.py
├── urls.py
├── navigation.py
├── search/interface_profile.py
├── graphql/interface_profile.py
├── template_content.py      # PluginTemplateExtension subclasses
├── api/
│   ├── serializers/interface_profile.py
│   ├── views/interface_profile.py
│   └── urls.py
├── migrations/
├── templates/netbox_interface_profiles/
└── testing/                 # Reusable base test classes (not type-checked)
```

Each `__init__.py` re-exports from its sub-modules. When adding a new model, add a corresponding `<modelname>.py` file in each component directory and update the `__init__.py`.

### Full-stack object checklist

When adding a new model, implement **all** of the following — do not stop at the model:

1. **Model** — inherit from `NetBoxModel`; implement `__str__` and `get_absolute_url`; use `models.TextChoices` for choice fields
2. **Table** — inherit from `NetBoxTable`; include `pk`, `id`, and `actions` in `fields`
3. **Forms** — four forms: `NetBoxModelForm`, `NetBoxModelFilterSetForm`, `NetBoxModelImportForm`, `NetBoxModelBulkEditForm`
4. **FilterSet** — inherit `NetBoxModelFilterSet`; implement `search()` method
5. **UI Views** — full CRUD: `ObjectView`, `ObjectListView`, `ObjectEditView`, `ObjectDeleteView`, `BulkImportView`, `BulkEditView`, `BulkDeleteView`
6. **URLs** — include changelog and journal routes (`ObjectChangeLogView`, `ObjectJournalView`)
7. **Template** — extend `generic/object.html`; use HTMX/Tailwind (NetBox v4 stack, not Bootstrap)
8. **API Serializer** — include `url`, `display`, and `brief_fields` in `Meta`
9. **API ViewSet** — inherit `NetBoxModelViewSet`
10. **API URLs** — use `NetBoxRouter`
11. **Navigation** — register via `PluginMenuItem` / `PluginMenuButton`
12. **Search** — register with `@register_search` / `SearchIndex`
13. **GraphQL** (optional) — `NetBoxObjectType` + `Query` class; registered via `graphql_schema = "graphql.schema"` in `PluginConfig`

### Extending core NetBox views

To attach a tab to an existing NetBox model view, use `register_model_view` + `ViewTab`:

```python
from utilities.views import ViewTab, register_model_view

@register_model_view(SomeCoreModel, name='myview', path='my-path')
class MyView(generic.ObjectView):
    tab = ViewTab(label='My Tab', badge=lambda obj: ..., permission='...')
```

To inject content into core views, subclass `PluginTemplateExtension` in `template_content.py` and expose it as `template_extensions = [...]`.

### Testing base classes

`netbox_interface_profiles/testing/` provides reusable base classes:

- `PluginTestCase` — user/permission management, `assertHttpStatus`, `cleanupSubTest`
- `PluginModelTestCase` — `assertInstanceEqual`, `model_to_dict`
- `PluginAPITestCase` — token auth, `_get_list_url`, `_get_detail_url`
- `PluginViewTestCase` — `_get_url`, `post_data`
- `PluginGraphQLTestCase` — `execute_query`, `assertGraphQLSuccess`

Always test both with and without required permissions.

## Code Conventions

- **Python 3.12+ syntax**: use `str | None` not `Optional[str]`, use f-strings, use strict type hints on all methods.
- **Line length**: 120 characters (ruff configured).
- `__init__.py` files are exempt from `F401` (unused imports) — they serve as re-export surfaces.
- API serializers must always expose `display` (read-only) and `url` fields, plus define `brief_fields` in `Meta`.
- Background jobs must use `netbox.jobs`.
