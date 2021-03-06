# Generated by Django 2.2.10 on 2020-05-28 13:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0515_auto_20200519_1649'),
        ('learning_unit', '0002_learningclassyear_changed'),
    ]

    operations = [
        migrations.CreateModel(
            name='CentralManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('with_child', models.BooleanField(default=False)),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_unit',
                                             to='base.Entity')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_unit',
                                             to='base.Person')),
            ],
            options={
                'verbose_name': 'Central manager',
                'verbose_name_plural': 'Central managers',
                'default_related_name': 'learning_unit',
            },
        ),
    ]
