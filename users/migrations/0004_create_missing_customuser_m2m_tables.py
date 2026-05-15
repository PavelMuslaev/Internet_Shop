from django.db import migrations


def create_missing_customuser_m2m_tables(apps, schema_editor):
    CustomUser = apps.get_model("users", "CustomUser")
    existing_tables = set(schema_editor.connection.introspection.table_names())

    for through_model in (CustomUser.groups.through, CustomUser.user_permissions.through):
        if through_model._meta.db_table not in existing_tables:
            schema_editor.create_model(through_model)


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_alter_customuser_managers"),
    ]

    operations = [
        migrations.RunPython(
            create_missing_customuser_m2m_tables,
            migrations.RunPython.noop,
        ),
    ]
