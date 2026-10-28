---
title: Interface roles
description: Create roles and role groups, and assign roles to interfaces.
sidebar:
  order: 1
---

An **interface role** describes what an interface is used for. It has a name, an optional description, an
optional [role group](#role-groups) and optional [device roles](#availability).

## Role groups

A role group bundles roles with the same operational impact, for example `access` for end-user ports and `trunk`
for uplinks. Groups have no behaviour of their own: they exist so [permissions](../permissions/) can be
constrained on them, letting a team assign only the roles of certain groups.

## Availability

When assigning a role from the device's **Interface Roles** tab, only roles that apply are offered:

- **Device roles**: a role with device roles is only offered on devices with one of those device roles. A role
  without device roles is offered on all devices.
- **Config templates**: the role button on an interface's row additionally only offers a role with
  [config templates](../config-templates/) when at least one of them is in scope of the interface, i.e. matches
  the device's platform, device type and tags and the interface's tags. A role without config templates is
  offered everywhere.

Roles the user is not permitted to assign are left out of **Assign Role** and shown disabled in the row menu. The
assignment forms, bulk import and the REST API do not apply these availability filters, only the
[permission constraints](../permissions/).

## Assigning roles

Every interface has at most one role. There are several ways to assign it:

Device **Interface Roles** tab
: Lists all interfaces of the device, or of all members of its virtual chassis, with their role. Select
  interfaces and click **Assign Role** or **Remove Role** to change them in bulk, or use the role button on a row
  to change a single interface.

Assignments list
: **Interface Roles → Assignments** lists all assignments, with the usual add, bulk edit, bulk delete and
  CSV/YAML/JSON import.

REST API
: Create, change or delete objects at `/api/plugins/netbox-interface-profiles/interface-role-assignments/`.
  See the [REST API reference](../../reference/api/).

## What happens on assignment

Creating or changing an assignment applies the role's [interface template](../interface-templates/) to the
interface right away. If the result is not a valid NetBox interface, for example because the template sets a
mode the interface type does not support, the request fails with an error and the assignment is not saved.

Removing an assignment leaves the interface as it is.

The interface's detail page shows an **Interface Role Automation** card with the role, the interface template
that applies, the config template that applies, and a preview of the rendered configuration.

## Deleting roles

A role cannot be deleted while interfaces are assigned to it. Remove or change the assignments first. Deleting a
role deletes its interface templates, config templates and synchronization records.
