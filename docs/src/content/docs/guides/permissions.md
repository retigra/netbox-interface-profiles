---
title: Permissions
description: Control who may assign which roles with NetBox object permissions.
sidebar:
  order: 5
---

Assigning a role reconfigures the interface, so who may assign which role is controlled with regular NetBox
[object permissions](https://netboxlabs.com/docs/netbox/administration/permissions/) on **Interface Role
Assignment**.

## Delegating by role group

Put roles in a [role group](../interface-roles/#role-groups), e.g. `access` and `trunk`, and constrain the
permissions on that group:

| Permission                 | Object type               | Actions             | Constraints                                 |
| -------------------------- | ------------------------- | ------------------- | ------------------------------------------- |
| Service desk: access ports | Interface Role Assignment | add, change, delete | `{"interface_role__group__slug": "access"}` |
| Network engineering        | Interface Role Assignment | add, change, delete | _(none)_                                    |

Both also need `view` on Interface Role Assignment, Interface Role and Interface.

Constraints can be combined with any other attribute of the assignment, for example to limit a team to one site:

```json
{"interface_role__group__slug": "access", "interface__device__site__slug": "ams01"}
```

## How constraints are enforced

Constraints apply to the assignment both **before and after** a change. With the service desk permission above, a
user can therefore not change or clear an interface that currently has a trunk role, not even to an access role.

Constraints are enforced everywhere assignments are written:

- the device **Interface Roles** tab and the per-interface role menu,
- the assignment add and edit forms,
- bulk import and bulk edit,
- the REST API.

The device tab and the role menu only offer the roles the user may assign.

## Other permissions

| Task                                   | Required permissions                                                         |
| -------------------------------------- | ---------------------------------------------------------------------------- |
| See the device **Interface Roles** tab | `netbox_interface_profiles.view_interfaceroleassignment`                     |
| Synchronize a role                     | `dcim.change_interface`, `netbox_interface_profiles.view_rolesync`           |
| View synchronizations                  | `netbox_interface_profiles.view_rolesync`                                    |
| Sync a config template from its data file | `netbox_interface_profiles.sync_profileconfigtemplate`                    |

Managing roles, groups and templates uses the standard add, change and delete permissions of each object type.
