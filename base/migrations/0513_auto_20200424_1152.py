# Generated by Django 2.2.10 on 2020-04-24 11:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0512_cte_manager'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='educationgroup',
            options={'permissions': (('add_training', 'Can add training'), ('add_minitraining', 'Can add mini-training'), ('add_group', 'Can add group'), ('change_commonpedagogyinformation', 'Can change common pedagogy information'), ('change_pedagogyinformation', 'Can change pedagogy information'), ('change_link_data', 'Can change link data')), 'verbose_name': 'Education group'},
        ),
    ]
