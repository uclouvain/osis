# Generated by Django 2.2.13 on 2020-09-03 14:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0533_remove_educationgroupyear_main_teaching_campus'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='educationgroupyear',
            name='constraint_type',
        ),
        migrations.RemoveField(
            model_name='educationgroupyear',
            name='max_constraint',
        ),
        migrations.RemoveField(
            model_name='educationgroupyear',
            name='min_constraint',
        ),
    ]