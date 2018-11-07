from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0383_organizationaddress_is_main'),
    ]

    operations = [
        TrigramExtension(),
    ]
