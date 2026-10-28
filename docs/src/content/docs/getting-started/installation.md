---
title: Installation
description: Install the plugin in NetBox or netbox-docker.
sidebar:
  order: 2
---

## Requirements

- NetBox 4.7. See [compatibility](../../reference/compatibility/) for the versions each release supports.
- Python 3.12 or later.
- A running NetBox worker (`manage.py rqworker`), because role synchronizations run as background jobs.

The plugin has no Python dependencies beyond those of NetBox.

## Install the package

While the plugin is not yet published on PyPI, install it from GitHub into the virtual environment of NetBox:

```bash
source /opt/netbox/venv/bin/activate
pip install git+https://github.com/wouterdebruijn/netbox-interface-profiles
```

To keep the plugin installed when NetBox is upgraded, add it to `local_requirements.txt` in the NetBox root:

```bash
echo "git+https://github.com/wouterdebruijn/netbox-interface-profiles" >> /opt/netbox/local_requirements.txt
```

### netbox-docker

Add the package to `plugin_requirements.txt` and rebuild the image, as described in the
[netbox-docker plugin instructions](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins):

```text title="plugin_requirements.txt"
git+https://github.com/wouterdebruijn/netbox-interface-profiles
```

## Enable the plugin

Add the plugin to `PLUGINS` in `configuration.py`:

```python title="configuration.py"
PLUGINS = [
    "netbox_interface_profiles",
]
```

The plugin has no required settings. An empty entry in `PLUGINS_CONFIG` is enough:

```python title="configuration.py"
PLUGINS_CONFIG = {
    "netbox_interface_profiles": {},
}
```

## Apply migrations

Create the plugin's database tables, collect its static files and restart NetBox and its worker:

```bash
cd /opt/netbox/netbox
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart netbox netbox-rq
```

The **Interface Roles** menu now appears in the navigation, and devices have an **Interface Roles** tab.

:::note
The **Interface Roles** tab replaces the device's **Interfaces** tab for users who can view role assignments.
It lists the same interfaces with their role, and offers all the bulk actions of the original tab. The original
tab is still reachable through its URL, and shows a notice pointing to the new tab.
:::
