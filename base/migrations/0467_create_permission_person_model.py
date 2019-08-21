from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0466_auto_20190730_1101'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'permissions': (
                ('is_administrator', 'Is administrator'),
                ('is_institution_administrator', 'Is institution administrator '),
                ('can_edit_education_group_administrative_data', 'Can edit education group administrative data'),
                ('can_manage_charge_repartition', 'Can manage charge repartition'),
                ('can_manage_attribution', 'Can manage attribution'),
                ('can_read_persons_roles', 'Can read persons roles'))
            },
        ),
    ]
