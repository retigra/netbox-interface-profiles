---
title: Jinja helpers
description: Functions the plugin adds to every template NetBox renders.
sidebar:
  order: 2
---

The plugin adds these functions to the Jinja2 environment of NetBox, so they are available in device config
templates, export templates and any other template NetBox renders.

## `interface_config_render(interface, **kwargs)`

Renders the [config template](../../guides/config-templates/) that applies to `interface` with the highest weight,
and returns the output as a string. Returns an empty string when the interface has no role or no config template
applies.

The config template receives the context of the calling template, such as `device` and the device's config context,
plus `interface` and the keyword arguments:

```jinja
{{ interface_config_render(interface, uplink_vlan=10) }}
```

## `interface_role_get(interface)`

Returns the interface role of the applicable config template with the highest weight, or `None` when no config
template applies. Because a config template's role is the interface's role, this is the interface's role whenever
it has a config template.

```jinja
{% set role = interface_role_get(interface) %}
{% if role and role.group and role.group.slug == "trunk" %}
  spanning-tree portfast trunk
{% endif %}
```

:::note
An interface whose role has no applicable config template returns `None`. Use
`interface.role_assignment.interface_role` to get the assigned role regardless of config templates.
:::

## Python

The same matching is available in Python, for example in custom scripts:

```python
from netbox_interface_profiles.models import ProfileConfigTemplate

# Applicable config templates, highest weight first
templates = ProfileConfigTemplate.objects.for_interface(interface)

# Config templates in scope of the interface, for any role
templates = ProfileConfigTemplate.objects.in_scope(interface)
```
