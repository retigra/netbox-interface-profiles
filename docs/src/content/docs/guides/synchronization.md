---
title: Synchronization
description: Apply changed interface templates to every interface with a role, with a dry run first.
sidebar:
  order: 3
---

Interface templates are applied when a role is assigned. After changing a template, **synchronize** the role to
apply the change to every interface that already has it.

## Running a synchronization

1. Open the role and click **Synchronize Role**.
2. Keep **Dry run** enabled to only calculate the changes, or disable it to save them right away.
3. Start the synchronization. It runs as a background job, so a NetBox worker must be running.

You are taken to the synchronization's page, which updates once the job has finished.

## Reviewing a dry run

A dry run lists every interface that would change, with the old and new value of each changed attribute. Nothing
has been saved yet. Click **Apply Changes** to run the synchronization for real.

:::note
Applying a dry run starts a new synchronization, which recalculates the changes. Edits made to templates or
interfaces after the dry run are taken into account.
:::

## Failures

A synchronization runs in a single database transaction. If any interface cannot be changed, for example because
the result is not a valid interface, the job fails, every change is rolled back, and the page shows which interface
caused the error.

## History

Every synchronization, including dry runs, is recorded. Find them under **Interface Roles → Synchronizations**, or
on the **Synchronizations** tab of a role. A record keeps the device and interface names, so it stays readable
after an interface is renamed or deleted. Delete old records from the list when you no longer need them.

## Permissions

Starting a synchronization requires `dcim.change_interface` and `netbox_interface_profiles.view_rolesync`. Viewing
synchronizations requires `netbox_interface_profiles.view_rolesync`.
