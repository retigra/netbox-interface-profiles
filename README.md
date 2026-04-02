# netbox-interface-profiles

NetBox plugin for managing interface configuration profiles.

## Features

_Features will be documented as they are developed._

## Screenshots

_Screenshots will be added as features are developed._

## Compatibility

This plugin requires **NetBox 4.5**.

| NetBox Version | Plugin Version |
| -------------- | -------------- |
| 4.5.x          | 0.1.0          |

For more detailed compatibility information, see [COMPATIBILITY.md](COMPATIBILITY.md).

## Dependencies

- NetBox 4.5+
- Python 3.12 or later

No additional Python packages are required beyond NetBox's core dependencies.

## Installing

While this plugin is in development and not yet published to PyPI, install directly from GitHub:

```bash
pip install git+https://github.com/wouterdebruijn/netbox-interface-profiles
```

Or add to your `local_requirements.txt` / `plugin_requirements.txt` (netbox-docker):

```
git+https://github.com/wouterdebruijn/netbox-interface-profiles
```

Enable the plugin in your NetBox `configuration.py`:

```python
PLUGINS = [
    'netbox_interface_profiles'
]
```

For adding to a NetBox Docker setup, see the
[general instructions for using netbox-docker with plugins](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

## Development

A Docker Compose environment is provided for local development. It runs a full NetBox stack with the plugin installed in editable mode and hot reloading enabled — no image rebuilds are needed when changing plugin code.

See [docker/README.md](docker/README.md) for setup instructions, how to run tests, and how to create and apply database migrations.

## Configuration

This plugin does not require any additional configuration by default. Optional parameters can be added to `PLUGINS_CONFIG` in your NetBox configuration file:

```python
PLUGINS_CONFIG = {
    "netbox_interface_profiles": {},
}
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Bugs and feature requests can be submitted via [GitHub Issues](https://github.com/wouterdebruijn/netbox-interface-profiles/issues).

## Credits

Based on the NetBox plugin tutorial:

- [demo repository](https://github.com/netbox-community/netbox-plugin-demo)
- [tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin)
project template.
