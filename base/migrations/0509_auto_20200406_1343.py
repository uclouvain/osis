# Generated by Django 2.2.10 on 2020-04-06 13:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0508_auto_20200325_1013'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='educationgroup',
            options={'permissions': (('add_training', 'Can add training'), ('add_minitraining', 'Can add mini-training'), ('add_group', 'Can add group'), ('change_commonpedagogyinformation', 'Can change common pedagogy information'), ('change_pedagogyinformation', 'Can change pedagogy information'), ('change_educationgroupcontent', 'Can change education group content')), 'verbose_name': 'Education group'},
        ),
    ]
