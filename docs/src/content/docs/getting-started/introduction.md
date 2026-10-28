---
title: Introduction
description: What NetBox Interface Profiles does and how its objects relate to each other.
sidebar:
  order: 1
---

NetBox Interface Profiles adds **interface roles** to NetBox. A role describes what an interface is used for,
such as an access port for workstations, a port for access points or an uplink. Assigning a role to an interface
configures it: the plugin applies the role's interface attributes and VLANs, and renders the configuration the
device needs for that interface.

## Objects

The plugin adds these objects, all under the **Interface Roles** menu:

| Object                        | Purpose                                                                                                        |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **Role Group**                | Groups roles by impact, e.g. `access` and `trunk`, to delegate who may assign them.                            |
| **Interface Role**            | What an interface is used for. Optionally limited to devices with certain device roles.                        |
| **Interface Role Assignment** | Links one interface to one role.                                                                               |
| **Interface Template**        | The NetBox interface attributes and VLANs a role applies, globally or for a site group or site.                |
| **Config Template**           | The Jinja2 template that renders the device configuration of an interface with a role, per platform.           |
| **Role Synchronization**      | A record of one synchronization run of a role, including dry runs, listing every interface it changed.         |

They relate as follows:

```text
Role Group ─┬─ Interface Role ─┬─ Interface Template   (attributes + VLANs, per scope)
            │                  ├─ Config Template      (Jinja2, per platform)
            │                  └─ Assignment ── Interface
            └─ ...
```

## How it works

1. You create a role, for example `Workstation`, and give it an interface template that sets the mode to
   access and the untagged VLAN to VID 100.
2. You assign the role to interfaces on the device's **Interface Roles** tab. Each assignment applies the
   interface template immediately: the interfaces become access ports in the VLAN with VID 100 of their site.
3. When the role changes, for example the VLAN moves to VID 110, you edit the template and
   [synchronize](../../guides/synchronization/) the role. A dry run shows every interface that would change
   before anything is saved.
4. Device config templates call `interface_config_render(interface)` to embed the rendered configuration of
   each interface in the device configuration.

Continue with the [installation](../installation/), or follow the [quick start](../quick-start/) for a
walkthrough.
