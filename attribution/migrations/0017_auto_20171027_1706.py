# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-27 15:06
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0157_entitymanager_entity'),
        ('attribution', '0016_auto_20171018_0937'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False)),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('function', models.CharField(blank=True, choices=[('COORDINATOR', 'COORDINATOR'), ('HOLDER', 'HOLDER'), ('CO_HOLDER', 'CO_HOLDER'), ('DEPUTY', 'DEPUTY'), ('DEPUTY_AUTHORITY', 'DEPUTY_AUTHORITY'), ('DEPUTY_SABBATICAL', 'DEPUTY_SABBATICAL'), ('DEPUTY_TEMPORARY', 'DEPUTY_TEMPORARY'), ('PROFESSOR', 'PROFESSOR'), ('INTERNSHIP_SUPERVISOR', 'INTERNSHIP_SUPERVISOR'), ('INTERNSHIP_CO_SUPERVISOR', 'INTERNSHIP_CO_SUPERVISOR')], db_index=True, max_length=35, null=True)),
                ('volume_lecturing', models.DecimalField(blank=True, decimal_places=1, max_digits=6, null=True)),
                ('volume_pratical_exercice', models.DecimalField(blank=True, decimal_places=1, max_digits=6, null=True)),
                ('learning_container_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.LearningContainerYear')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Tutor')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='tutorapplication',
            unique_together=set([('learning_container_year', 'tutor', 'function')]),
        ),
    ]
