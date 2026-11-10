from django.db import migrations, models

# The relation holding the objects in scope, by the model of the scope type
SCOPE_RELATIONS = {
    "site": "scope_sites",
    "sitegroup": "scope_site_groups",
}


def copy_scopes(apps, schema_editor):
    """Move the single scope object of each template to the scope relation of its scope type."""
    InterfaceTemplate = apps.get_model("interface_profiles", "InterfaceTemplate")

    for template in InterfaceTemplate.objects.filter(scope_type__isnull=False).select_related("scope_type"):
        relation = getattr(template, SCOPE_RELATIONS[template.scope_type.model])
        if relation.model.objects.filter(pk=template.scope_id).exists():
            relation.add(template.scope_id)


def restore_scopes(apps, schema_editor):
    """Keep the first object in scope of each template, as the single scope of the previous version."""
    InterfaceTemplate = apps.get_model("interface_profiles", "InterfaceTemplate")

    for template in InterfaceTemplate.objects.filter(scope_type__isnull=False).select_related("scope_type"):
        relation = getattr(template, SCOPE_RELATIONS[template.scope_type.model])
        template.scope_id = relation.order_by("pk").values_list("pk", flat=True).first()
        template.save(update_fields=["scope_id"])


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0250_cooling_infrastructure"),
        ("interface_profiles", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="interfacetemplate",
            name="scope_sites",
            field=models.ManyToManyField(blank=True, related_name="interface_role_templates", to="dcim.site"),
        ),
        migrations.AddField(
            model_name="interfacetemplate",
            name="scope_site_groups",
            field=models.ManyToManyField(blank=True, related_name="interface_role_templates", to="dcim.sitegroup"),
        ),
        migrations.RunPython(copy_scopes, restore_scopes),
        migrations.RemoveField(
            model_name="interfacetemplate",
            name="scope_id",
        ),
    ]
