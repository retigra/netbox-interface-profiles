# interface-profiles

NetBox plugin for managing interface configuration profiles.

**Documentation: <https://wouterdebruijn.github.io/netbox-interface-profiles/>**

## Features

- [Interface roles](https://wouterdebruijn.github.io/netbox-interface-profiles/guides/interface-roles/):
  describe what an interface is for and assign it from the device page, in bulk,
  or through the REST API.
- [Interface templates](https://wouterdebruijn.github.io/netbox-interface-profiles/guides/interface-templates/):
  set speed, duplex, MTU, mode, PoE and VLANs per role, globally or per site
  group or site.
- [Synchronization](https://wouterdebruijn.github.io/netbox-interface-profiles/guides/synchronization/):
  apply changed templates to every interface with a role, with a dry run to
  review the changes first.
- [Config templates](https://wouterdebruijn.github.io/netbox-interface-profiles/guides/config-templates/):
  render per-interface device configuration with Jinja2.
- [Permissions](https://wouterdebruijn.github.io/netbox-interface-profiles/guides/permissions/):
  delegate which roles a team may assign with NetBox object permissions.

## Screenshots

_Screenshots will be added as features are developed._

## Compatibility

This plugin requires **NetBox 4.7**.

| NetBox Version | Plugin Version |
| -------------- | -------------- |
| 4.7.x          | 0.1.0          |

For more detailed compatibility information, see
[COMPATIBILITY.md](COMPATIBILITY.md).

## Dependencies

- NetBox 4.7+
- Python 3.12 or later

No additional Python packages are required beyond NetBox's core dependencies.

## Installing

While this plugin is in development and not yet published to PyPI, install
directly from GitHub:

```bash
pip install git+https://github.com/wouterdebruijn/netbox-interface-profiles
```

Or add to your `local_requirements.txt` / `plugin_requirements.txt`
(netbox-docker):

```
git+https://github.com/wouterdebruijn/netbox-interface-profiles
```

Enable the plugin in your NetBox `configuration.py`:

```python
PLUGINS = [
    'interface_profiles'
]
```

For adding to a NetBox Docker setup, see the
[general instructions for using netbox-docker with plugins](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

See the
[installation guide](https://wouterdebruijn.github.io/netbox-interface-profiles/getting-started/installation/)
for all steps, and the
[quick start](https://wouterdebruijn.github.io/netbox-interface-profiles/getting-started/quick-start/)
to set up a first role.

## Development

A Docker Compose environment is provided for local development. It runs a full
NetBox stack with the plugin installed in editable mode and hot reloading
enabled — no image rebuilds are needed when changing plugin code.

See [docker/README.md](docker/README.md) for setup instructions, how to run
tests, and how to create and apply database migrations, and
[Writing documentation](https://wouterdebruijn.github.io/netbox-interface-profiles/development/documentation/)
for previewing and editing the docs.

## Configuration

This plugin does not require any additional configuration by default. Optional
parameters can be added to `PLUGINS_CONFIG` in your NetBox configuration file:

```python
PLUGINS_CONFIG = {
    "interface_profiles": {},
}
```

## Config Templates

Config templates hold the Jinja2 template that renders the configuration of an
interface. Like NetBox's own config templates, the template code is either
stored locally or synchronized from a data file in a data source, optionally
automatically when the file changes. Environment parameters and debug output
work the same as well.

A config template applies to an interface when:

- its **interface role** is the role assigned to the interface,
- its **platform** is the platform of the device,
- its **device type** is empty or the device type of the device,
- all of its **device tags** are on the device, and all of its **interface
  tags** are on the interface.

When multiple config templates apply, the one with the highest **weight** is
used. `ProfileConfigTemplate.objects.for_interface(interface)` returns the
applicable templates, highest weight first.

NetBox config templates (and any other template rendered by NetBox) can render
the interface configuration with `interface_config_render(interface)`. It
renders the applicable template with the highest weight, or returns an empty
string when none applies. The interface template receives the context of the
calling template, such as `device` and the device's config context, plus
`interface` and any keyword arguments passed to `interface_config_render`.

`interface_role_get(interface)` returns the interface role of the applicable
config template with the highest weight, or `None` when none applies:

```jinja
hostname {{ device.name }}

{% for interface in device.interfaces.all() %}
{% set role = interface_role_get(interface) %}
interface {{ interface.name }}
{% if role %}
  description {{ role.name }}
{% endif %}
  {{ interface_config_render(interface) | indent(2) }}
{% endfor %}
```

See
[Config templates](https://wouterdebruijn.github.io/netbox-interface-profiles/guides/config-templates/)
and the
[Jinja helpers reference](https://wouterdebruijn.github.io/netbox-interface-profiles/reference/jinja-helpers/)
in the documentation.

## Permissions

Assigning a role reconfigures the interface, so who may assign which role is
controlled with regular NetBox object permissions on **Interface Role
Assignment**. Put roles in a **Role Group** (e.g. `access`, `trunk`) and
constrain the permissions on that group:

| Permission                 | Object type               | Actions             | Constraints                                 |
| -------------------------- | ------------------------- | ------------------- | ------------------------------------------- |
| Service desk: access ports | Interface Role Assignment | add, change, delete | `{"interface_role__group__slug": "access"}` |
| Network engineering        | Interface Role Assignment | add, change, delete | _(none)_                                    |

Both users also need `view` on Interface Role Assignment, Interface Role and
Interface.

Constraints apply to the assignment both before and after a change. A service
desk user with the permission above can therefore not change or clear an
interface that currently has a trunk role, not even to an access role.
Constraints can be combined with any other assignment attribute, e.g.
`{"interface_role__group__slug": "access", "interface__device__site__slug": "ams01"}`.

The constraints are enforced everywhere assignments are written: the device
**Interface Roles** tab, the per-interface menu, the assignment forms, bulk
import/edit and the REST API. The device tab and menu only offer the roles the
user may assign.

See
[Permissions](https://wouterdebruijn.github.io/netbox-interface-profiles/guides/permissions/)
in the documentation.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for
guidelines.

Bugs and feature requests can be submitted via
[GitHub Issues](https://github.com/wouterdebruijn/netbox-interface-profiles/issues).

## Credits

Based on the NetBox plugin tutorial:

- [demo repository](https://github.com/netbox-community/netbox-plugin-demo)
- [tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin)
project template.
