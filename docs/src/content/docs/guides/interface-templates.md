---
title: Interface templates
description: Define the interface attributes and VLANs a role applies, per site or site group.
sidebar:
  order: 2
---

An **interface template** holds the NetBox interface attributes a role applies. A role can have several
templates, each for a different [scope](#scope).

## Attributes

| Attribute         | Interface field   | Notes                                                                      |
| ----------------- | ----------------- | -------------------------------------------------------------------------- |
| Speed (Mbps)      | `speed`           | E.g. `1000` or `10000`.                                                    |
| Duplex            | `duplex`          | Auto, half or full.                                                        |
| MTU               | `mtu`             |                                                                            |
| Mode              | `mode`            | Access, tagged or tagged all.                                              |
| Enabled           | `enabled`         | Always applied.                                                            |
| POE mode          | `poe_mode`        |                                                                            |
| Untagged VLAN VID | `untagged_vlan`   | Resolved to a VLAN in the interface's site, see [VLANs](#vlans).           |
| Tagged VLAN VIDs  | `tagged_vlans`    | A list of VIDs, resolved the same way.                                     |

### Empty values

An empty attribute leaves the interface's value unchanged. To clear an interface attribute instead, leave the
value empty and enable its **Clear** option, e.g. **Clear MTU**. A template cannot both set a value and clear it.

Clearing the mode also removes the untagged and tagged VLANs of the interface, because NetBox only allows VLANs on
interfaces with a mode.

Tagged VLANs are always applied: an empty list removes all tagged VLANs from the interface.

## Scope

A template applies globally, to a **site group** or to a **site**. When a role has several templates, the most
specific one that matches the interface's site is used:

1. a template scoped to the device's site,
2. a template scoped to the site's site group,
3. a template without a scope.

Only one template is applied to an interface; attributes are not merged between templates. A role without a
matching template does not change the interface.

:::tip
Use a global template for the defaults and site-specific templates only where a site deviates, e.g. a site where
the workstation VLAN has a different VID.
:::

## VLANs

Templates store VLANs by **VID** rather than as VLAN objects, so one template works in every site even though each
site has its own VLAN objects. A VID is resolved to the first VLAN found:

1. a VLAN with that VID assigned to the device's site,
2. a VLAN with that VID in a VLAN group scoped to the site,
3. a VLAN with that VID in a VLAN group scoped to the site's site group.

VIDs that do not resolve to a VLAN are skipped: the untagged VLAN is cleared and missing tagged VLANs are left
out.

## When templates are applied

Templates are applied when a role is [assigned](../interface-roles/#what-happens-on-assignment) to an interface.
Editing a template does not change existing interfaces: [synchronize the role](../synchronization/) to apply the
changes to all interfaces that have it.
