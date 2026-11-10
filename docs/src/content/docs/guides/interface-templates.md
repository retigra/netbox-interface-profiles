---
title: Interface templates
description: Define the interface attributes and VLANs a role applies, per site or site group.
sidebar:
  order: 2
---

An **interface template** holds the NetBox interface attributes a role applies. A role can have several
templates, each for a different [scope](#scope).

## Attributes

| Attribute               | Interface field           | Notes                                                                       |
| ----------------------- | ------------------------- | --------------------------------------------------------------------------- |
| Enabled                 | `enabled`                 | Always applied.                                                             |
| Management only         | `mgmt_only`               | Yes, no, or empty to leave the interface unchanged.                         |
| Interface description   | `description`             | The template's own **Description** only describes the template.             |
| Speed (Kbps)            | `speed`                   | In Kbps, like NetBox, e.g. `1000000` for 1 Gbps. The form offers presets.   |
| Duplex                  | `duplex`                  | Auto, half or full.                                                         |
| MTU                     | `mtu`                     |                                                                             |
| VRF                     | `vrf`                     |                                                                             |
| 802.1Q mode             | `mode`                    | Access, tagged, tagged (all) or Q-in-Q.                                     |
| Untagged VLAN VID       | `untagged_vlan`           | Resolved to a VLAN in the interface's site, see [VLANs](#vlans).            |
| Tagged VLAN VIDs        | `tagged_vlans`            | VIDs and ranges, e.g. `100,200-205`. Requires the tagged mode.              |
| Q-in-Q SVLAN VID        | `qinq_svlan`              | Resolved to a service VLAN in the interface's site. Requires the Q-in-Q mode. |
| VLAN translation policy | `vlan_translation_policy` |                                                                             |
| PoE mode                | `poe_mode`                | PD or PSE.                                                                  |
| PoE type                | `poe_type`                | E.g. 802.3at (Type 2).                                                      |

Attributes that only make sense for one interface, such as the name, label, type, MAC address, LAG, parent or
cable, are not part of a template.

### Empty values

An empty attribute leaves the interface's value unchanged. To clear an interface attribute instead, leave the
value empty and enable its **Clear** option, e.g. **Clear MTU**. A template cannot both set a value and clear it.
Clearing the interface description sets it to an empty string.

Tagged VLANs are always applied: an empty list removes all tagged VLANs from the interface.

### Modes and VLANs

The template follows the rules NetBox applies to interfaces:

- Tagged VLANs can only be set with the tagged mode, and a Q-in-Q service VLAN only with the Q-in-Q mode. A template
  that sets another mode together with these VLANs cannot be saved.
- Clearing the mode also removes the untagged VLAN, tagged VLANs and service VLAN of the interface, because NetBox
  only allows VLANs on interfaces with a mode. Such a template cannot set any VLANs.
- Changing the mode removes the VLANs the new mode does not allow: NetBox removes the tagged VLANs when the mode is
  not tagged, and the plugin removes the service VLAN when the mode is not Q-in-Q.
- A template without a mode that sets tagged VLANs or a service VLAN only applies to interfaces that are already in
  the right mode. On other interfaces, the assignment or synchronization fails with an error.

## Scope

A template applies globally, to one or more **site groups** or to one or more **sites**. A template has a single
scope type, so it cannot be scoped to sites and site groups at the same time. When a role has several templates,
the most specific one that matches the interface's site is used:

1. a template scoped to sites, including the device's site,
2. a template scoped to site groups, including the site's site group or one of its parent groups, the nearest group
   first,
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

The Q-in-Q service VLAN is resolved the same way, but only among VLANs with the Q-in-Q role **Service**.

VIDs that do not resolve to a VLAN are skipped: the untagged VLAN and service VLAN are cleared and missing tagged
VLANs are left out.

## Importing templates

Templates can be imported as CSV, JSON or YAML from the template list. Refer to the role by name, the VRF by its
route distinguisher and the VLAN translation policy by name. The objects in scope are referred to by ID in
`scope_ids` or by name in `scope_names`, like NetBox's `scope_id` and `scope_name`. Tagged VLANs are written like in
the form:

```yaml
- interface_role: Workstation
  name: Amsterdam
  scope_type: dcim.site
  scope_names: [Amsterdam, Rotterdam]
  mode: tagged
  untagged_vlan_vid: 100
  tagged_vlans_vids: "200,300-305"
  poe_mode: pse
  set_null_mtu: true
```

## When templates are applied

Templates are applied when a role is [assigned](../interface-roles/#what-happens-on-assignment) to an interface.
Editing a template does not change existing interfaces: [synchronize the role](../synchronization/) to apply the
changes to all interfaces that have it.
