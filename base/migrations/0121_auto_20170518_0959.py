# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-05-18 07:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0120_students_groups'),
    ]

    operations = [
        migrations.RenameField(
            model_name='learningcomponentyear',
            old_name='hourly_volume_Q1',
            new_name='hourly_volume_partial',
        ),
    ]
