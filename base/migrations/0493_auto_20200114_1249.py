# Generated by Django 2.2.5 on 2020-01-14 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0492_populate_empty_english_title_in_education_group_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationgroupyear',
            name='weighting',
            field=models.BooleanField(default=True, verbose_name='Weighting'),
        ),
    ]