# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-12-17 09:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0417_auto_20181214_0955'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hops',
            name='uuid',
        ),
    ]
