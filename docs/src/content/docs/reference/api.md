---
title: REST API and GraphQL
description: Endpoints, filters and GraphQL queries provided by the plugin, and how to use them in automation.
sidebar:
  order: 1
---

All plugin objects are available through NetBox's REST and GraphQL APIs, with the same authentication, filtering,
brief mode, field selection and bulk operations as core NetBox objects. The interactive API documentation at
`/api/schema/swagger-ui/` lists every field and filter.

## REST endpoints

All endpoints are under `/api/plugins/interface-profiles/`.

| Endpoint                      | Object                                                                    |
| ----------------------------- | ------------------------------------------------------------------------- |
| `role-groups/`                | Role Group                                                                |
| `interface-roles/`            | Interface Role                                                            |
| `interface-role-assignments/` | Interface Role Assignment                                                 |
| `interface-templates/`        | Interface Template                                                        |
| `profile-config-templates/`   | Config Template                                                           |
| `interface-configs/`          | Role and rendered configuration of an interface (read-only), see [below](#interface-configuration) |

The examples below use `curl` with a NetBox API token:

```bash
export NETBOX_URL=https://netbox.example.com
export NETBOX_TOKEN=nbt_...
```

## Interface configuration

`interface-configs/` is a read-only endpoint built for automation. Pass it an **interface ID** and it returns, in
one call:

- the interface,
- its role assignment and interface role,
- the [interface template](../../guides/interface-templates/) that applies to it,
- the [config template](../../guides/config-templates/) that applies to it, and
- the configuration rendered by that config template.

```bash
curl -s -H "Authorization: Bearer $NETBOX_TOKEN" \
  "$NETBOX_URL/api/plugins/interface-profiles/interface-configs/123/"
```

```json
{
  "id": 123,
  "url": "https://netbox.example.com/api/plugins/interface-profiles/interface-configs/123/",
  "display": "Gi1/0/1",
  "interface": {
    "id": 123,
    "name": "Gi1/0/1",
    "device": { "id": 12, "name": "sw01", "...": "..." },
    "...": "..."
  },
  "role_assignment": { "id": 45, "url": "...", "display": "Gi1/0/1 → Workstation" },
  "interface_role": {
    "id": 4,
    "name": "Workstation",
    "description": "",
    "group": { "id": 1, "name": "Access", "slug": "access", "...": "..." },
    "...": "..."
  },
  "interface_template": { "id": 7, "name": "Default", "description": "", "...": "..." },
  "config_template": { "id": 3, "name": "IOS access port", "weight": 1000, "...": "..." },
  "config": "switchport mode access\nswitchport access vlan 100\nspanning-tree portfast",
  "config_error": null
}
```

| Field                | Value                                                                                                    |
| -------------------- | -------------------------------------------------------------------------------------------------------- |
| `id`                 | The ID of the interface.                                                                                 |
| `interface`          | The interface, as returned by NetBox's own interface endpoint in brief mode.                             |
| `role_assignment`    | The assignment linking the interface to its role, or `null` when it has no role.                         |
| `interface_role`     | The role of the interface, or `null`.                                                                    |
| `interface_template` | The interface template that applies to the interface, or `null` when none matches.                       |
| `config_template`    | The config template with the highest weight that applies to the interface, or `null` when none matches. |
| `config`             | The rendered configuration, or `null` when no config template applies or rendering failed.              |
| `config_error`       | The rendering error when the config template could not be rendered, otherwise `null`.                   |

An interface without a role is returned with all role fields set to `null`, so the endpoint can be queried for any
interface.

### Rendering context

The configuration is rendered the same way as when a device config template calls
[`interface_config_render()`](../jinja-helpers/#interface_config_renderinterface-kwargs): the config template
receives the device's **config context**, `device` and `interface`. `role`, `assignment` and `config_template` are
available as well.

A template that fails to render does not fail the request. The error is returned in `config_error`, formatted like
NetBox formats config template errors: a full traceback when the config template has **Debug** enabled, a concise
message otherwise.

### Listing and filtering

Without an ID the endpoint lists interfaces. It accepts every filter of NetBox's `/api/dcim/interfaces/` endpoint,
plus these filters on the role:

| Filter                    | Example                         |
| ------------------------- | ------------------------------- |
| `interface_role_id`       | `?interface_role_id=4`          |
| `interface_role`          | `?interface_role=Workstation`   |
| `interface_role_group_id` | `?interface_role_group_id=1`    |
| `interface_role_group`    | `?interface_role_group=access`  |
| `has_interface_role`      | `?has_interface_role=true`      |

For example, the configuration of every interface with a role on one device:

```bash
curl -s -H "Authorization: Bearer $NETBOX_TOKEN" \
  "$NETBOX_URL/api/plugins/interface-profiles/interface-configs/?device=sw01&has_interface_role=true&limit=0"
```

Add `?brief=true` to return only the `id`, `url`, `display` and `interface_role` of each interface. Brief mode does not
render the configuration, which makes it the fastest way to look up roles. Use `?fields=` to select other fields,
e.g. `?fields=id,interface_role,config`.

### Permissions

The endpoint requires the `dcim.view_interface` permission and only returns interfaces the user may view. The role,
templates and configuration are only returned when the user may also view the interface's role assignment
(`interface_profiles.view_interfaceroleassignment`); otherwise these fields are `null`.

### pynetbox

```python
import pynetbox

nb = pynetbox.api("https://netbox.example.com", token="nbt_...")
configs = nb.plugins.interface_profiles.interface_configs

# One interface
result = configs.get(123)
if result.interface_role:
    print(result.interface_role.name)
    print(result.config)

# All interfaces with a role on a device
for result in configs.filter(device="sw01", has_interface_role=True):
    print(result.interface.name, result.interface_role.name)
    if result.config_error:
        raise RuntimeError(f"{result.interface.name}: {result.config_error}")
```

:::tip
pynetbox derives the attribute from the URL: the `interface-profiles` plugin becomes `interface_profiles` and the
`interface-configs` endpoint becomes `interface_configs`.
:::

## Role assignments

### Looking up the role of an interface

When only the role is needed, filter the assignments on the interface. The interface and role are returned as
nested objects:

```bash
curl -s -H "Authorization: Bearer $NETBOX_TOKEN" \
  "$NETBOX_URL/api/plugins/interface-profiles/interface-role-assignments/?interface_id=123"
```

```json
{
  "count": 1,
  "results": [
    {
      "id": 45,
      "display": "Gi1/0/1 → Workstation",
      "interface": { "id": 123, "name": "Gi1/0/1", "device": { "id": 12, "name": "sw01", "...": "..." }, "...": "..." },
      "interface_role": { "id": 4, "name": "Workstation", "group": { "slug": "access", "...": "..." }, "...": "..." },
      "...": "..."
    }
  ]
}
```

An empty result means the interface has no role. Assignments can be filtered on:

| Filter                    | Example                                  |
| ------------------------- | ---------------------------------------- |
| `interface_id`            | `?interface_id=123`                      |
| `interface`               | `?device=sw01&interface=Gi1/0/1`         |
| `device_id`               | `?device_id=12`                          |
| `device`                  | `?device=sw01`                           |
| `interface_role_id`       | `?interface_role_id=4`                   |
| `interface_role`          | `?interface_role=Workstation`            |
| `interface_role_group_id` | `?interface_role_group_id=1`             |
| `interface_role_group`    | `?interface_role_group=access`           |

### Assigning a role

Create an assignment with the IDs of the interface and the role. As in the UI, the role's interface template is
applied in the same request, and the request fails when the result is not a valid interface.

```bash
curl -X POST \
  -H "Authorization: Bearer $NETBOX_TOKEN" \
  -H "Content-Type: application/json" \
  "$NETBOX_URL/api/plugins/interface-profiles/interface-role-assignments/" \
  --data '{"interface": 123, "interface_role": 4}'
```

To change the role, `PATCH` the assignment with a new `interface_role`. To remove it, `DELETE` the assignment.
[Permission constraints](../../guides/permissions/) apply to all of these.

## Interface templates

Interface templates are scoped with `scope_type` (`dcim.site` or `dcim.sitegroup`) and `scope_id`. Leave both empty
for a global template. VLANs are set by VID, and choice fields take the same values as NetBox's interface endpoint:

```json
{
  "interface_role": 4,
  "name": "Amsterdam",
  "scope_type": "dcim.site",
  "scope_id": 12,
  "interface_description": "Workstation",
  "mode": "tagged",
  "untagged_vlan_vid": 100,
  "tagged_vlans_vids": [200, 201],
  "poe_mode": "pse",
  "poe_type": "type2-ieee802.3at",
  "set_null_mtu": true
}
```

See [Interface templates](../../guides/interface-templates/#attributes) for every attribute. Besides the attributes
themselves, templates can be filtered on `interface_role`, `scope_site_id`, `scope_site_group_id`, `is_global` and
`tagged_vlan_vid`.

## GraphQL

Each object has a single and a list query:

| Query                                                         | Object                    |
| ------------------------------------------------------------- | ------------------------- |
| `role_group`, `role_group_list`                               | Role Group                |
| `interface_role`, `interface_role_list`                       | Interface Role            |
| `interface_role_assignment`, `interface_role_assignment_list` | Interface Role Assignment |
| `interface_role_template`, `interface_role_template_list`     | Interface Template        |
| `profile_config_template`, `profile_config_template_list`     | Config Template           |

The interface template queries are named `interface_role_template` because NetBox already has an
`interface_template` query for device type components.

```graphql
{
  interface_role_list {
    name
    group { slug }
    interface_assignments { interface { name device { name } } }
  }
}
```

Rendered configuration and role synchronizations are not available through GraphQL. Use the
[`interface-configs/`](#interface-configuration) REST endpoint to get the rendered configuration.
