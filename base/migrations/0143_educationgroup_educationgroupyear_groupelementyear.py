# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-13 13:15
from __future__ import unicode_literals

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0016_auto_20170410_1318'),
        ('base', '0142_auto_20170718_1145'),
    ]

    operations = [
        migrations.CreateModel(
            name='EducationGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EducationGroupYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('acronym', models.CharField(db_index=True, max_length=15)),
                ('title', models.CharField(max_length=255)),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.AcademicYear')),
                ('education_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroup')),
                ('education_group_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.OfferType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GroupElementYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('child_branch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_branch', to='base.EducationGroupYear')),
                ('child_leaf', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_leaf', to='base.EducationGroupYear')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent', to='base.EducationGroupYear')),
                ('learning_unit_year', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.LearningUnitYear')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
