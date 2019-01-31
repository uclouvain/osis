from django.db import migrations, connection


def get_migration_sql(table_name):
    new_table_name = table_name.replace('core_', 'base_')
    return "ALTER TABLE IF EXISTS {old_table_name} RENAME TO {new_table_name};".format(old_table_name=table_name,
                                                                                       new_table_name=new_table_name)


def migrate_table_name():
    tables = connection.introspection.table_names()
    return [migrations.RunSQL(get_migration_sql(table_name)) for table_name in tables if
            table_name.startswith('core_')]


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    migrate_app_label = migrations.RunSQL(
        """DO $$
        BEGIN
            IF EXISTS (select * from pg_class where relname='django_content_type') THEN
                UPDATE django_content_type SET app_label='base' WHERE app_label='core';
            END IF;
        END;
        $$;"""
    )

    update_migration_table = migrations.RunSQL(
        """DO $$
        BEGIN
            IF EXISTS (select * from pg_class where relname='django_migrations') THEN
                UPDATE django_migrations SET app='base' WHERE app='core';
            END IF;
        END;
        $$;"""
    )

    operations = [migrate_app_label] + migrate_table_name() + [update_migration_table]