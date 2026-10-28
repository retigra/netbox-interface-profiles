---
title: Config templates
description: Render the device configuration of interfaces with Jinja2, per platform, device type and tags.
sidebar:
  order: 4
---

A **config template** holds the Jinja2 template that renders the configuration of an interface with a role. Where
[interface templates](../interface-templates/) set NetBox interface attributes, config templates produce the text
that goes into the device configuration.

Config templates work like NetBox's own config templates: the template code is stored in NetBox or synchronized
from a file in a [data source](https://netboxlabs.com/docs/netbox/models/core/datasource/), optionally
automatically when the file changes. Environment parameters and the **Debug** option work the same as well.

## Matching

A config template applies to an interface when:

- its **interface role** is the role assigned to the interface,
- its **platform** is the platform of the device,
- its **device type** is empty or the device type of the device,
- all of its **device tags** are on the device, and
- all of its **interface tags** are on the interface.

When several config templates apply, the one with the highest **weight** is used. The default weight is `1000`.
Devices without a platform never match a config template.

:::tip
Create one template per platform with the default weight, and add templates with a higher weight and a device type
or tags for the exceptions.
:::

## Writing a template

A config template is rendered with:

| Variable    | Value                                                                                                 |
| ----------- | ----------------------------------------------------------------------------------------------------- |
| `interface` | The interface being rendered.                                                                         |
| _caller_    | Everything in the context of the template that renders it, e.g. `device` and the device config context. |
| _arguments_ | Keyword arguments passed to `interface_config_render()`.                                              |

The output is plain text, so autoescaping is always disabled.

```jinja title="Access port (Cisco IOS)"
description {{ interface.description or interface.role_assignment.interface_role.name }}
switchport mode access
switchport access vlan {{ interface.untagged_vlan.vid }}
spanning-tree portfast
{% if not interface.enabled %}
shutdown
{% endif %}
```

## Embedding in device configuration

NetBox device config templates render each interface's configuration with `interface_config_render()`, and get its
role with `interface_role_get()`:

```jinja title="Device config template"
hostname {{ device.name }}

{% for interface in device.interfaces.all() %}
{% set role = interface_role_get(interface) %}
interface {{ interface.name }}
{% if role %}
  description {{ role.name }}
{% endif %}
  {{ interface_config_render(interface, role=role) | indent(2) }}
{% endfor %}
```

Interfaces without an applicable config template render as an empty string. See the
[Jinja helpers reference](../../reference/jinja-helpers/) for details.

## Preview

The **Interface Role Automation** card on an interface's detail page lists the config templates that apply, marks
the one that is used, and shows a preview of its rendered output. The preview is rendered with `interface`,
`device`, `role`, `assignment` and `config_template`, but without the device's config context.
