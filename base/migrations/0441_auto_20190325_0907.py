# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-03-25 09:07
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0440_validationrule_placeholder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationaddress',
            name='city',
            field=models.CharField(max_length=255, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='organizationaddress',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference.Country', verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='organizationaddress',
            name='label',
            field=models.CharField(max_length=20, verbose_name='Label'),
        ),
        migrations.AlterField(
            model_name='organizationaddress',
            name='location',
            field=models.CharField(max_length=255, verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='organizationaddress',
            name='postal_code',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Postal code'),
        ),
    ]
