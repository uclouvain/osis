# Generated by Django 2.2.5 on 2019-12-17 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0488_auto_20191211_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.EmailField(default='', max_length=255),
        ),
    ]
