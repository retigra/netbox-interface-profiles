---
title: REST API and GraphQL
description: Endpoints and GraphQL queries provided by the plugin.
sidebar:
  order: 1
---

All plugin objects are available through NetBox's REST and GraphQL APIs, with the same authentication, filtering,
brief mode and bulk operations as core NetBox objects. The interactive API documentation at `/api/schema/swagger-ui/`
lists every field.

## REST endpoints

All endpoints are under `/api/plugins/netbox-interface-profiles/`.

| Endpoint                      | Object                    |
| ----------------------------- | ------------------------- |
| `role-groups/`                | Role Group                |
| `interface-roles/`            | Interface Role            |
| `interface-role-assignments/` | Interface Role Assignment |
| `interface-templates/`        | Interface Template        |
| `profile-config-templates/`   | Config Template           |

### Assigning a role

Create an assignment with the IDs of the interface and the role. As in the UI, the role's interface template is
applied in the same request, and the request fails when the result is not a valid interface.

```bash
curl -X POST \
  -H "Authorization: Bearer $NETBOX_TOKEN" \
  -H "Content-Type: application/json" \
  https://netbox.example.com/api/plugins/netbox-interface-profiles/interface-role-assignments/ \
  --data '{"interface": 123, "interface_role": 4}'
```

To change the role, `PATCH` the assignment with a new `interface_role`. To remove it, `DELETE` the assignment.
[Permission constraints](../../guides/permissions/) apply to all of these.

### Interface templates

Interface templates are scoped with `scope_type` (`dcim.site` or `dcim.sitegroup`) and `scope_id`. Leave both empty
for a global template. VLANs are set by VID:

```json
{
  "interface_role": 4,
  "name": "Amsterdam",
  "scope_type": "dcim.site",
  "scope_id": 12,
  "mode": "tagged",
  "untagged_vlan_vid": 100,
  "tagged_vlans_vids": [200, 201]
}
```

## GraphQL

Each object has a single and a list query:

| Query                                                          | Object                    |
| -------------------------------------------------------------- | ------------------------- |
| `role_group`, `role_group_list`                                | Role Group                |
| `interface_role`, `interface_role_list`                        | Interface Role            |
| `interface_role_assignment`, `interface_role_assignment_list`  | Interface Role Assignment |
| `interface_role_template`, `interface_role_template_list`      | Interface Template        |
| `profile_config_template`, `profile_config_template_list`      | Config Template           |

```graphql
{
  interface_role_list {
    name
    group { slug }
    interface_assignments { interface { name device { name } } }
  }
}
```

Role synchronizations are not exposed through the APIs.
