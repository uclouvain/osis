# Generated by Django 2.2.13 on 2020-11-20 10:40

from django.db import migrations
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0542_delete_organizationaddress'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organization',
            options={'ordering': (django.db.models.expressions.OrderBy(django.db.models.expressions.F('is_active'), descending=True), 'name'), 'permissions': (('can_access_organization', 'Can access organization'),)},
        ),
    ]
