---
title: Contributing
description: Set up a development environment and run the tests.
sidebar:
  order: 1
---

Contributions are welcome. Report bugs and request features in
[GitHub Issues](https://github.com/wouterdebruijn/netbox-interface-profiles/issues), and see
[CONTRIBUTING.md](https://github.com/wouterdebruijn/netbox-interface-profiles/blob/main/CONTRIBUTING.md) for the
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
docker compose exec netbox ./manage.py makemigrations netbox_interface_profiles
```

See [docker/README.md](https://github.com/wouterdebruijn/netbox-interface-profiles/blob/main/docker/README.md) for
details.

## Tests and linting

```bash
docker compose exec netbox ./manage.py test netbox_interface_profiles.tests --keepdb
make lint
make format
```

CI runs Ruff and the test suite against every supported Python version on each push and pull request.
