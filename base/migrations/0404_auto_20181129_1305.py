# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-29 13:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0403_perms_for_sic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examenrollment',
            name='date_enrollment',
            field=models.DateField(null=True, verbose_name="Date d'inscription"),
        ),
    ]
