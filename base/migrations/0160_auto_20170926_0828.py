# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-26 06:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0159_learning_component_year_not_null'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='academicyear',
            options={'ordering': ['year'], 'permissions': (('can_access_academicyear', 'Can access academic year'),)},
        ),
    ]
