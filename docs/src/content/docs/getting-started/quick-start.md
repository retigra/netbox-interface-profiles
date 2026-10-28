---
title: Quick start
description: Create a role, give it an interface template and assign it to interfaces.
sidebar:
  order: 3
---

This walkthrough creates a `Workstation` role that turns interfaces into access ports in VLAN 100. It assumes a
device in a site that has a VLAN with VID 100, either assigned to the site or in a VLAN group scoped to the site
or its site group.

## 1. Create a role group

Go to **Interface Roles → Role Groups** and add a group named `Access`. Groups are optional, but they are how
you [delegate assignment permissions](../../guides/permissions/), so it is easiest to use them from the start.

## 2. Create a role

Go to **Interface Roles → Interface Roles** and add a role:

| Field        | Value                           |
| ------------ | ------------------------------- |
| Name         | `Workstation`                   |
| Group        | `Access`                        |
| Device roles | _empty: available on all devices_ |

## 3. Add an interface template

Go to **Interface Roles → Interface Templates** and add a template:

| Field          | Value                             |
| -------------- | --------------------------------- |
| Interface role | `Workstation`                     |
| Name           | `Default`                         |
| Scope type     | _empty: applies to every site_    |
| Mode           | Access                            |
| Untagged VLAN VID | `100`                          |
| Enabled        | Yes                               |

## 4. Assign the role

Open a device and go to its **Interface Roles** tab. Select a few interfaces, click **Assign Role** and choose
`Workstation`. You can also assign a role to a single interface with the role button on its row.

Each assignment applies the interface template right away. Open one of the interfaces: its mode is now
_Access_, its untagged VLAN is the VLAN with VID 100 of the device's site, and its detail page shows the
**Interface Role Automation** card with the role and the template that was applied.

## 5. Change the role

Edit the `Default` template and change the untagged VLAN to `110`. Existing interfaces do not change until you
synchronize the role: open the `Workstation` role, click **Synchronize Role** and start a dry run. The result lists
every interface that would change, with its old and new values. Click **Apply Changes** to save them.

## Next steps

- Learn how templates are [scoped to sites and site groups](../../guides/interface-templates/#scope).
- Render device configuration with [config templates](../../guides/config-templates/).
- Let the service desk assign access roles with [permissions](../../guides/permissions/).
