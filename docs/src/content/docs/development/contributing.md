---
title: Contributing
description: Set up a development environment and run the tests.
sidebar:
  order: 1
---

Contributions are welcome. Report bugs and request features in
[GitHub Issues](https://github.com/retigra/netbox-interface-profiles/issues), and see
[CONTRIBUTING.md](https://github.com/retigra/netbox-interface-profiles/blob/main/CONTRIBUTING.md) for the
pull request guidelines.

## Development environment

The `docker/` directory contains a Docker Compose stack with NetBox, a worker, PostgreSQL and Valkey. The plugin is
installed in editable mode and NetBox runs Django's development server, so code changes reload without rebuilding
the image.

```bash
cd docker
docker compose up
```

NetBox is available at <http://localhost:8000>. Migrations are applied on startup. After changing models, create
the migration with:

```bash
docker compose exec netbox ./manage.py makemigrations interface_profiles
```

See [docker/README.md](https://github.com/retigra/netbox-interface-profiles/blob/main/docker/README.md) for
details.

## Tests and linting

From the repository root:

```bash
make docker-test                                       # all tests, with the CI configuration
make docker-test TESTS=interface_profiles.tests.test_api  # a single module
make lint
make format
```

`make docker-test` runs the tests in a throwaway NetBox container against the PostgreSQL and Valkey services of the
development environment, using a separate test database.

CI runs Ruff, checks for missing migrations and runs the test suite against every supported NetBox version on each push
and pull request.

## Releasing

Releases are tagged `vX.Y.Z`. A tag publishes the package to PyPI and the documentation of that version to `/X.Y/`
and `/latest/`. See the release checklist in
[CONTRIBUTING.md](https://github.com/retigra/netbox-interface-profiles/blob/main/CONTRIBUTING.md#releasing).
