import django.db.models.deletion
from django.db import migrations, models

# Renamed relations that may be referenced by object permission constraints, e.g. "interface_profile__group__slug"
CONSTRAINT_LOOKUPS = {
    "interface_profile": "interface_role",
    "interface_profile_id": "interface_role_id",
    "interface_profiles": "interface_roles",
    "profile_assignment": "role_assignment",
}


def _rename_lookups(constraints, renames: dict[str, str]):
    if isinstance(constraints, list):
        return [_rename_lookups(item, renames) for item in constraints]
    if isinstance(constraints, dict):
        return {
            "__".join(renames.get(part, part) for part in key.split("__")): value for key, value in constraints.items()
        }
    return constraints


def _update_permission_constraints(apps, schema_editor, renames: dict[str, str]):
    ObjectPermission = apps.get_model("users", "ObjectPermission")
    for permission in ObjectPermission.objects.using(schema_editor.connection.alias).exclude(constraints=None):
        constraints = _rename_lookups(permission.constraints, renames)
        if constraints != permission.constraints:
            permission.constraints = constraints
            permission.save(update_fields=["constraints"])


def forwards_constraints(apps, schema_editor):
    _update_permission_constraints(apps, schema_editor, CONSTRAINT_LOOKUPS)


def backwards_constraints(apps, schema_editor):
    _update_permission_constraints(apps, schema_editor, {new: old for old, new in CONSTRAINT_LOOKUPS.items()})


class Migration(migrations.Migration):
    dependencies = [
        ("interface_profiles", "0006_interfacetemplate_set_null"),
        ("users", "0011_concrete_objecttype"),
    ]

    operations = [
        migrations.RenameModel(old_name="InterfaceProfile", new_name="InterfaceRole"),
        migrations.RenameModel(old_name="InterfaceProfileAssignment", new_name="InterfaceRoleAssignment"),
        migrations.RenameModel(old_name="ProfileGroup", new_name="RoleGroup"),
        migrations.RenameModel(old_name="ProfileSync", new_name="RoleSync"),
        migrations.RenameModel(old_name="ProfileSyncChange", new_name="RoleSyncChange"),
        migrations.RenameField(
            model_name="interfaceroleassignment", old_name="interface_profile", new_name="interface_role"
        ),
        migrations.RenameField(model_name="rolesync", old_name="interface_profile", new_name="interface_role"),
        # RenameField does not update constraint fields, so the constraint is recreated around the rename
        migrations.RemoveConstraint(
            model_name="interfacetemplate",
            name="unique_template_name_per_profile",
        ),
        migrations.RenameField(model_name="interfacetemplate", old_name="interface_profile", new_name="interface_role"),
        migrations.AlterModelOptions(
            name="interfacetemplate",
            options={"ordering": ("interface_role", "name")},
        ),
        migrations.AddConstraint(
            model_name="interfacetemplate",
            constraint=models.UniqueConstraint(fields=("interface_role", "name"), name="unique_template_name_per_role"),
        ),
        migrations.AlterField(
            model_name="interfacerole",
            name="device_roles",
            field=models.ManyToManyField(blank=True, related_name="interface_roles", to="dcim.devicerole"),
        ),
        migrations.AlterField(
            model_name="interfacerole",
            name="group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="interface_roles",
                to="interface_profiles.rolegroup",
            ),
        ),
        migrations.AlterField(
            model_name="interfaceroleassignment",
            name="interface",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, related_name="role_assignment", to="dcim.interface"
            ),
        ),
        migrations.AlterField(
            model_name="rolesync",
            name="job",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, related_name="interface_role_sync", to="core.job"
            ),
        ),
        migrations.RunPython(forwards_constraints, backwards_constraints),
    ]
