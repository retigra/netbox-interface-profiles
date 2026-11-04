---
title: Compatibility
description: Supported NetBox and Python versions per release, and how to upgrade.
sidebar:
  order: 3
---

| Plugin version | Minimum NetBox version | Maximum NetBox version | Python |
| -------------- | ---------------------- | ---------------------- | ------ |
| 0.1.x          | 4.7.0                  | 4.7.99                 | 3.12+  |

Use the version selector at the top of the page to read the documentation of the plugin version you run.

## Upgrading

1. Read the [release notes of the plugin](https://github.com/retigra/netbox-interface-profiles/blob/main/CHANGELOG.md)
   and of [NetBox](https://netboxlabs.com/docs/netbox/release-notes/) for breaking changes.
2. Test the upgrade in a development environment.
3. Back up the database.
4. Upgrade the package and apply migrations:

   ```bash
   pip install --upgrade interface-profiles
   cd /opt/netbox/netbox
   python manage.py migrate
   python manage.py collectstatic --no-input
   ```

5. Restart NetBox and its worker.
