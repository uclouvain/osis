# Generated by Django 2.2.13 on 2021-01-05 09:32

from django.db import migrations


def delete_in_charge_from_initial_data(apps, schema_editor):
    ProposalLearningUnit = apps.get_model('base', 'ProposalLearningUnit')

    proposals = ProposalLearningUnit.objects.filter(initial_data__learning_container_year__isnull=False)

    for proposal in proposals:
        to_delete = proposal.initial_data['learning_container_year'].get('in_charge')
        if to_delete is not None:
            init_data = proposal.initial_data
            del init_data['learning_container_year']['in_charge']
            proposal.initial_data = init_data
            proposal.save()


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0555_merge_20210113_0756'),
    ]

    operations = [
        migrations.RunPython(delete_in_charge_from_initial_data),
    ]