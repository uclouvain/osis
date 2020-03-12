# Generated by Django 2.2.10 on 2020-03-12 11:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('education_group', '0005_auto_20200128_1246'),
        ('base', '0507_auto_20200303_1341'),
        ('program_management', '0002_auto_20200124_2055'),
    ]

    operations = [
        migrations.CreateModel(
            name='EducationGroupVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('is_transition', models.BooleanField(verbose_name='Transition')),
                ('version_name', models.CharField(blank=True, max_length=100, verbose_name='Version name')),
                ('title_fr', models.CharField(blank=True, max_length=255, null=True, verbose_name='Title in French')),
                ('title_en', models.CharField(blank=True, max_length=255, null=True, verbose_name='Title in English')),
                ('offer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.EducationGroupYear', verbose_name='Offer')),
                ('root_group', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='education_group.GroupYear', verbose_name='Root group')),
            ],
            options={
                'unique_together': {('version_name', 'offer')},
            },
        ),
        migrations.AlterModelManagers(
            name='educationgroupversion',
            managers=[
                ('standard', django.db.models.manager.Manager()),
            ],
        ),
    ]
