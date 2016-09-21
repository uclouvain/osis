# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-02 16:58
from __future__ import unicode_literals
from django.core.management.sql import emit_post_migrate_signal

from django.db import migrations


def add_internship_access_to_student_group(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    emit_post_migrate_signal(2, False, db_alias)
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    student_group = Group.objects.get(name='students')
    # Add permissions to group
    internships_perm = Permission.objects.get(codename='can_access_internship')
    student_group.permissions.add(internships_perm)


def add_init_internship_manager_group(apps, schema_editor):
    # create group
    db_alias = schema_editor.connection.alias
    emit_post_migrate_signal(2, False, db_alias)
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    internship_manager_group, created = Group.objects.get_or_create(name='internship_manager')
    if created:
        # Add permissions to group
        student_path_perm = Permission.objects.get(codename='can_access_student_path')
        internships_perm = Permission.objects.get(codename='can_access_internship')
        internship_manager_perm = Permission.objects.get(codename='is_internship_manager')
        internship_manager_group.permissions.add(student_path_perm, internships_perm, internship_manager_perm)


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0013_create_internship_access_perm'),
        ('contenttypes', '__latest__'),
    ]

    operations = [
        migrations.RunPython(add_internship_access_to_student_group),
        migrations.RunPython(add_init_internship_manager_group),
    ]
