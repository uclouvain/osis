# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-08-07 15:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0471_auto_20190806_1143'),
    ]

    operations = [
        migrations.RenameField(
            model_name='educationgroup',
            old_name='new_end_year',
            new_name='end_year',
        ),
        migrations.RenameField(
            model_name='educationgroup',
            old_name='new_start_year',
            new_name='start_year',
        ),
    ]
