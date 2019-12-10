# Generated by Django 2.2.5 on 2019-12-06 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0486_message templates_postponements_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'auth_user_groups',
                'managed': False,
            },
        ),
        migrations.AlterField(
            model_name='academiccalendar',
            name='reference',
            field=models.CharField(choices=[('DELIBERATION', 'Deliberation'), ('DISSERTATION_SUBMISSION', 'Dissertation submission'), ('EXAM_ENROLLMENTS', 'Exam enrollments'), ('SCORES_EXAM_DIFFUSION', 'Scores exam diffusion'), ('SCORES_EXAM_SUBMISSION', 'Scores exam submission'), ('TEACHING_CHARGE_APPLICATION', 'Teaching charge application'), ('COURSE_ENROLLMENT', 'Course enrollment'), ('SUMMARY_COURSE_SUBMISSION', 'Summary course submission'), ('EDUCATION_GROUP_EDITION', 'Education group edition'), ('LEARNING_UNIT_EDITION_FACULTY_MANAGERS', 'Learning unit edition by faculty managers'), ('TESTING', 'Testing'), ('RELEASE', 'Release')], max_length=50),
        ),
    ]
