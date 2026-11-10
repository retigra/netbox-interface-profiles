# Changelog

All notable changes to this project are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed

- The **Interface Roles** menu only shows the items a user may view, and the
  Add and Import buttons only to users who may add those objects. The menu is
  hidden entirely from users without any of these permissions.
- The **Synchronize Role** button is only shown to users who may synchronize,
  and the related template tables on a role only to users who may view them.
- The interface page only shows the role card to users who may view the
  interface's role assignment, and only lists the templates, and renders the
  config preview, they may view.
- The role button on each row of the device **Interface Roles** tab is only
  shown to users who may add, change or delete role assignments.
- Assigning roles from the device tab and the role menu, and synchronizing a
  role, require view permission on that interface role.
- Synchronizing a role is rejected when it would change an interface outside
  the user's `dcim.change_interface` constraints, instead of changing every
  interface with the role.

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
