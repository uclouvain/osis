# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-06-17 10:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0460_populate_container_entities'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='entitycontaineryear',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='entitycontaineryear',
            name='entity',
        ),
        migrations.RemoveField(
            model_name='entitycontaineryear',
            name='learning_container_year',
        ),
        migrations.DeleteModel(
            name='EntityContainerYear',
        ),
    ]
