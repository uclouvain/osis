# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-20 09:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0206_sessionexamdeadline_deliberation_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationgroupyear',
            name='acronym',
            field=models.CharField(db_index=True, max_length=40),
        ),
    ]
