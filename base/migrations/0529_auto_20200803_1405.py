# Generated by Django 2.2.13 on 2020-08-03 14:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0528_adapt_prerequisite_for_versions'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='educationgroupyear',
            unique_together={('partial_acronym', 'academic_year'), ('education_group', 'academic_year'), ('acronym', 'academic_year')},
        ),
    ]
