# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-08-02 11:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0466_auto_20190730_1101'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='programmanager',
            options={'permissions': (('view_programmanager', 'Can view program manager'),)},
        ),
    ]
