# Generated by Django 2.2.13 on 2021-01-12 10:41
import datetime

from django.db import migrations
from django.utils import timezone

from base.models.enums import academic_calendar_type


def remove_learning_unit_academic_calendar(apps, shema_editor):
    AcademicCalendar = apps.get_model('base', 'academiccalendar')
    AcademicCalendar.objects.filter(
        reference__in=[
            academic_calendar_type.SUMMARY_COURSE_SUBMISSION,
            academic_calendar_type.SUMMARY_COURSE_SUBMISSION_FORCE_MAJEURE,
        ]
    ).delete()


def create_learning_unit_academic_calendar(apps, shema_editor):
    """
    We will create all calendars which are mandatory to learning unit app
    """
    AcademicYear = apps.get_model('base', 'academicyear')
    AcademicCalendar = apps.get_model('base', 'academiccalendar')

    now = timezone.now()
    current_academic_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).last()
    if current_academic_year:
        qs = AcademicYear.objects.filter(year__gte=2015, year__lte=current_academic_year.year + 6)
        for ac_year in qs:
            _create_learning_unit_summary_edition_calendar(AcademicCalendar, ac_year)
            _create_learning_unit_force_majeur_summary_edition_calendar(AcademicCalendar, ac_year)


def _create_learning_unit_summary_edition_calendar(academic_calendar_cls, targeted_academic_year):
    academic_calendar_cls.objects.update_or_create(
        reference=academic_calendar_type.SUMMARY_COURSE_SUBMISSION,
        data_year=targeted_academic_year,
        defaults={
            "title": "Edition fiches descriptives",
            "start_date": datetime.date(targeted_academic_year.year, 7, 1),
            "end_date": datetime.date(targeted_academic_year.year, 9, 13),
            "academic_year": targeted_academic_year  # To remove after refactoring
        }
    )


def _create_learning_unit_force_majeur_summary_edition_calendar(academic_calendar_cls, targeted_academic_year):
    academic_calendar_cls.objects.update_or_create(
        reference=academic_calendar_type.SUMMARY_COURSE_SUBMISSION_FORCE_MAJEURE,
        data_year=targeted_academic_year,
        defaults={
            "title": "Edition fiches descriptives (cas de force majeure)",
            "start_date": datetime.date(targeted_academic_year.year, 6, 15),
            "end_date": datetime.date(targeted_academic_year.year, 6, 20),
            "academic_year": targeted_academic_year  # To remove after refactoring
        }
    )


class Migration(migrations.Migration):

    dependencies = [
        ('learning_unit', '0005_role_migration_centralmanager_facultymanager'),
    ]

    operations = [
        migrations.RunPython(create_learning_unit_academic_calendar, remove_learning_unit_academic_calendar),
    ]
