# Generated by Django 2.2.13 on 2021-01-14 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0556_remove_in_charge_fix'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningunityear',
            name='other_remark_english',
            field=models.TextField(blank=True, null=True, verbose_name='Other remark in english (intended for publication)'),
        ),
    ]