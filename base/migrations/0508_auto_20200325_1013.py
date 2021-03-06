# Generated by Django 2.2.10 on 2020-03-25 10:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0507_auto_20200316_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupelementyear',
            name='quadrimester_derogation',
            field=models.CharField(blank=True, choices=[('Q1', 'Q1'), ('Q2', 'Q2'), ('Q3', 'Q3'), ('Q1and2', 'Q1 and Q2'), ('Q1or2', 'Q1 or Q2')], max_length=10, null=True, verbose_name='Quadrimester derogation'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='acronym',
            field=models.CharField(db_index=True, max_length=15, validators=[django.core.validators.RegexValidator('^[BEGLMTWX][A-Z]{2,4}[1-9]\\d{3}')], verbose_name='Code'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='quadrimester',
            field=models.CharField(blank=True, choices=[('Q1', 'Q1'), ('Q2', 'Q2'), ('Q3', 'Q3'), ('Q1and2', 'Q1 and Q2'), ('Q1or2', 'Q1 or Q2')], max_length=9, null=True, verbose_name='Quadrimester'),
        ),
    ]
