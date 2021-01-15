# Generated by Django 2.2.13 on 2021-01-11 13:55
import uuid

from django.db import migrations


def create_domain_isced(apps, schema_editor):
    DomainIsced = apps.get_model('reference', 'DomainIsced')
    DomainIsced.objects.update_or_create(
        code="9999",
        defaults={
            "uuid": uuid.uuid4(),
            "title_fr": "Toutes disciplines",
            "title_en": "All subject areas",
            "is_ares": False
        }
    )


def remove_domain_isced(apps, schema_editor):
    DomainIsced = apps.get_model('reference', 'DomainIsced')
    DomainIsced.objects.filter(code="9999").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0004_domainisced_is_ares'),
    ]

    operations = [
        migrations.RunPython(create_domain_isced, remove_domain_isced)
    ]