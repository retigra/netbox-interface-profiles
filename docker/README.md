# Docker Development Environment

This directory contains a Docker Compose setup that provides a full NetBox development environment with the `interface-profiles` plugin installed and configured for hot reloading.

## Services

| Service | Image | Port |
|---|---|---|
| `netbox` | Custom (based on `netboxcommunity/netbox:latest`) | `8000` |
| `netbox-worker` | Same as `netbox` | — |
| `postgres` | `postgres:17-alpine` | — |
| `valkey` | `valkey/valkey:9.0-alpine` | — |

## Getting started

From the `docker/` directory (or pass `-f docker/docker-compose.yml`):

```bash
cd docker
docker compose up
```

NetBox will be available at <http://localhost:8000>.

A superuser is created automatically on first boot. Check the NetBox Docker documentation or `super_user.py` inside the container for the default credentials.

## Hot reloading

The plugin is installed in **editable mode** (`uv pip install -e /opt/interface-profiles`) on every container start. The entire repository root is bind-mounted into the container at `/opt/interface-profiles`, so any change to the plugin's Python source is immediately reflected without rebuilding the image.

NetBox runs via Django's development server (`manage.py runserver`) instead of gunicorn, which means it automatically reloads when Python files change. `DEBUG=true` and `DEVELOPER=true` are set in the environment.

## Database migrations

Migrations are applied automatically on startup (including after plugin updates). To manage migrations manually:

**Create migrations** after changing models:

```bash
docker compose exec -it netbox ./manage.py makemigrations interface_profiles
```

**Apply pending migrations:**

```bash
docker compose exec -it netbox ./manage.py migrate
```

## Configuration

`configuration.py` is bind-mounted read-only into `/etc/netbox/config/configuration.py`. It reads all standard NetBox settings from environment variables, which are defined in `docker-compose.yml`.

The plugin is enabled via the `PLUGINS` list in `configuration.py`:

```python
PLUGINS = [
    "interface_profiles",
]
```

## Data persistence

PostgreSQL data is stored in a named Docker volume (`postgres_data`) and survives container restarts. To reset the database entirely:

```bash
docker compose down -v
```
