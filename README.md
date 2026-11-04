# Interface Profiles

A NetBox plugin that gives interfaces a **role**, such as an access port or an
uplink, and configures them from it: interface attributes, VLANs and the
rendered device configuration follow the role.

**Documentation: <https://retigra.github.io/netbox-interface-profiles/>**

## Features

- [Interface roles](https://retigra.github.io/netbox-interface-profiles/latest/guides/interface-roles/):
  describe what an interface is for and assign it from the device page, in bulk,
  or through the REST API.
- [Interface templates](https://retigra.github.io/netbox-interface-profiles/latest/guides/interface-templates/):
  set the description, speed, duplex, MTU, VRF, 802.1Q mode, VLANs, VLAN
  translation policy and PoE per role, globally or per site group or site. VLANs
  are set by VID and resolved in the interface's site.
- [Synchronization](https://retigra.github.io/netbox-interface-profiles/latest/guides/synchronization/):
  apply changed templates to every interface with a role, with a dry run to
  review the changes first.
- [Config templates](https://retigra.github.io/netbox-interface-profiles/latest/guides/config-templates/):
  render per-interface device configuration with Jinja2, per platform, device
  type and tags, and embed it in NetBox device config templates.
- [Permissions](https://retigra.github.io/netbox-interface-profiles/latest/guides/permissions/):
  delegate which roles a team may assign with NetBox object permissions.
- [REST API and GraphQL](https://retigra.github.io/netbox-interface-profiles/latest/reference/api/):
  every object is available through the APIs, and a single call returns the
  role and rendered configuration of an interface for automation.

## Compatibility

| NetBox Version | Plugin Version | Python |
| -------------- | -------------- | ------ |
| 4.7.x          | 0.1.x          | 3.12+  |

See [COMPATIBILITY.md](COMPATIBILITY.md) for details. The plugin has no Python
dependencies beyond those of NetBox.

## Installing

Install the package into the virtual environment of NetBox:

```bash
source /opt/netbox/venv/bin/activate
pip install netbox-interface-profiles
```

For netbox-docker, add `netbox-interface-profiles` to `plugin_requirements.txt`, see
the
[netbox-docker plugin instructions](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

Enable the plugin in `configuration.py`. It has no required settings:

```python
PLUGINS = [
    "interface_profiles",
]
```

Apply the migrations, collect the static files and restart NetBox and its
worker. Role synchronizations run as background jobs, so a NetBox worker
(`manage.py rqworker`) must be running.

```bash
cd /opt/netbox/netbox
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart netbox netbox-rq
```

See the
[installation guide](https://retigra.github.io/netbox-interface-profiles/latest/getting-started/installation/)
for all steps, and the
[quick start](https://retigra.github.io/netbox-interface-profiles/latest/getting-started/quick-start/)
to set up a first role.

## Automation

The `interface-configs` endpoint returns the role, the matching templates and
the rendered configuration of an interface by its ID:

```bash
curl -H "Authorization: Bearer $NETBOX_TOKEN" \
  https://netbox.example.com/api/plugins/interface-profiles/interface-configs/123/
```

```json
{
  "id": 123,
  "interface": { "id": 123, "name": "Gi1/0/1", "...": "..." },
  "interface_role": { "id": 4, "name": "Workstation", "...": "..." },
  "interface_template": { "id": 7, "name": "Default", "...": "..." },
  "config_template": { "id": 3, "name": "IOS access port", "...": "..." },
  "config": "switchport mode access\nswitchport access vlan 100",
  "config_error": null
}
```

It supports all of NetBox's interface filters, e.g.
`?device=sw01&has_interface_role=true`. See the
[REST API reference](https://retigra.github.io/netbox-interface-profiles/latest/reference/api/).

## Development

A Docker Compose environment runs a full NetBox stack with the plugin installed
in editable mode and hot reloading enabled. See
[docker/README.md](docker/README.md), [TESTING.md](TESTING.md) and
[Writing documentation](https://retigra.github.io/netbox-interface-profiles/latest/development/documentation/).

```bash
cd docker && docker compose up   # NetBox at http://localhost:8000
make docker-test                 # run the test suite
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for
guidelines. Bugs and feature requests can be submitted via
[GitHub Issues](https://github.com/retigra/netbox-interface-profiles/issues).
Changes are listed in the [changelog](CHANGELOG.md).

## Credits

Based on the NetBox plugin tutorial
([demo repository](https://github.com/netbox-community/netbox-plugin-demo),
[tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)), and
created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin)
project template.

## License

Licensed under the [GNU Affero General Public License v3.0](LICENSE).
