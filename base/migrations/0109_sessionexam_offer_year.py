# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-04-28 21:37
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0108_auto_20170428_1818'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionexam',
            name='offer_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.OfferYear'),
        ),
    ]
