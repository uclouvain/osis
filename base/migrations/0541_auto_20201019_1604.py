# Generated by Django 2.2.13 on 2020-10-19 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0540_prevent_empty_address'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='educationgroupyear',
            index_together={('partial_acronym', 'academic_year'), ('acronym', 'academic_year')},
        ),
    ]
