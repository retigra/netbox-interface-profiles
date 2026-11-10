# Changelog

All notable changes to this project are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- **Breaking:** an interface template can be scoped to several sites or several
  site groups. Like the scope of a NetBox VLAN group, the form has a single
  scope field to select the object type and then the objects, one or more here.
  In the REST API and in imports, `scope_id` is replaced by the list
  `scope_ids`, and the API returns the objects in scope as `scopes` instead of
  `scope`. Imports also accept `scope_names`. GraphQL exposes the objects as
  `scope_sites` and `scope_site_groups`. Existing scopes are migrated.
- Interface templates scoped to a site group also apply to sites in its child
  groups. When several site groups match, the template of the nearest group is
  used.

## [0.1.0] - 2026-11-04

First public release, for NetBox 4.7.

### Added

- **Interface roles** and **role groups**: describe what an interface is for,
  and assign one role per interface from the device's **Interface Roles** tab,
  the interface page, in bulk, by import or through the REST API.
- **Interface templates**: the interface attributes a role applies, globally or
  per site group or site: enabled, management only, description, speed, duplex,
  MTU, VRF, 802.1Q mode, untagged and tagged VLANs and the Q-in-Q service VLAN
  (by VID, resolved in the interface's site), VLAN translation policy, PoE mode
  and PoE type. Every nullable attribute can be explicitly cleared.
- **Synchronization**: apply changed templates to every interface with a role as
  a background job, with a dry run that lists every change before it is saved.
- **Config templates**: Jinja2 templates rendering the configuration of an
  interface per role and platform, optionally narrowed down by device type and
  tags, stored locally or synchronized from a data source. Device config
  templates embed them with `interface_config_render()`.
- **Permissions**: delegate which roles a team may assign with NetBox object
  permissions on role assignments.
- REST API and GraphQL for all objects, plus the read-only
  `interface-configs/` endpoint returning the role, matching templates and
  rendered configuration of an interface in a single call.

[Unreleased]: https://github.com/retigra/netbox-interface-profiles/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/retigra/netbox-interface-profiles/releases/tag/v0.1.0
