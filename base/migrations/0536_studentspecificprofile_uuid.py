# Generated by Django 2.2.13 on 2020-09-17 14:22

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0535_auto_20200908_1239'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentspecificprofile',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
