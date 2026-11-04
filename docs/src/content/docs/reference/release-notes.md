---
title: Release notes
description: What changed in each release of Interface Profiles.
sidebar:
  order: 4
---

Every release is also listed on [GitHub](https://github.com/retigra/netbox-interface-profiles/releases) and in the
[changelog](https://github.com/retigra/netbox-interface-profiles/blob/main/CHANGELOG.md). See
[compatibility](../compatibility/) for the NetBox versions each release supports and how to upgrade.

## 0.1.0

_Released 2026-11-04_

The first public release, for NetBox 4.7 and Python 3.12 or later. Install it from
[PyPI](https://pypi.org/project/netbox-interface-profiles/0.1.0/):

```bash
pip install netbox-interface-profiles==0.1.0
```

### Features

- **[Interface roles](../../guides/interface-roles/) and role groups**: describe what an interface is for, and assign
  one role per interface from the device's **Interface Roles** tab, the interface page, in bulk, by import or through
  the REST API.
- **[Interface templates](../../guides/interface-templates/)**: the interface attributes a role applies, globally or
  per site group or site: enabled, management only, description, speed, duplex, MTU, VRF, 802.1Q mode, untagged and
  tagged VLANs and the Q-in-Q service VLAN (by VID, resolved in the interface's site), VLAN translation policy, PoE
  mode and PoE type. Every nullable attribute can be explicitly cleared.
- **[Synchronization](../../guides/synchronization/)**: apply changed templates to every interface with a role as a
  background job, with a dry run that lists every change before it is saved.
- **[Config templates](../../guides/config-templates/)**: Jinja2 templates rendering the configuration of an interface
  per role and platform, optionally narrowed down by device type and tags, stored locally or synchronized from a data
  source. Device config templates embed them with [`interface_config_render()`](../jinja-helpers/).
- **[Permissions](../../guides/permissions/)**: delegate which roles a team may assign with NetBox object permissions
  on role assignments.
- **[REST API and GraphQL](../api/)** for all objects, plus the read-only `interface-configs/` endpoint returning the
  role, matching templates and rendered configuration of an interface in a single call.
