# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-08 10:31
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0003_decree_domain'),
    ]

    operations = [
        migrations.CreateModel(
            name='EducationInstitution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(max_length=100)),
                ('institution_type', models.CharField(choices=[('SECONDARY', 'Secondaire'), ('UNIVERSITY', 'University'), ('HIGHER_NON_UNIVERSITY', 'Higher non-university')], max_length=25)),
                ('postal_code', models.CharField(max_length=20)),
                ('city', models.CharField(max_length=255)),
                ('national_community', models.CharField(blank=True, choices=[('FRENCH', 'Communauté française de Belgique'), ('GERMAN', 'Communauté germanophone'), ('DUTCH', 'Communauté flamande')], max_length=20, null=True)),
                ('adhoc', models.BooleanField(default=False)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reference.Country')),
            ],
        ),
    ]
