# Generated by Django 2.2.13 on 2020-09-03 11:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0531_auto_20200902_1459'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='educationgroupyear',
            name='remark',
        ),
        migrations.RemoveField(
            model_name='educationgroupyear',
            name='remark_english',
        ),
    ]
