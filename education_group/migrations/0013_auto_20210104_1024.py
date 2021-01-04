# Generated by Django 2.2.13 on 2021-01-04 10:24
import datetime

from django.db import migrations
from django.utils import timezone

from base.models.enums import academic_calendar_type
from education_group.tasks import check_academic_calendar


def remove_education_group_academic_calendar(apps, shema_editor):
    AcademicCalendar = apps.get_model('base', 'academiccalendar')
    AcademicCalendar.objects.filter(
        reference__in=[
            academic_calendar_type.EDUCATION_GROUP_EDITION,
            academic_calendar_type.EDUCATION_GROUP_EXTENDED_DAILY_MANAGEMENT,
            academic_calendar_type.EDUCATION_GROUP_LIMITED_DAILY_MANAGEMENT,
        ]
    ).delete()


def create_education_group_academic_calendar(apps, shema_editor):
    """
    We will create all calendars which are mandatory to education group app
    """
    # Create calendars from N to N+6
    check_academic_calendar.run()

    # Create older calendars from EDUCATION_GROUP_EDITION to N
    AcademicYear = apps.get_model('base', 'academicyear')
    AcademicCalendar = apps.get_model('base', 'academiccalendar')

    now = timezone.now()
    current_academic_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).last()
    qs = AcademicYear.objects.filter(year__gte=2019, year__lt=current_academic_year.year)
    for ac_year in qs:
        _create_education_group_preparation_calendar(AcademicCalendar, ac_year)
        _create_education_group_extended_daily_management_calendar(AcademicCalendar, ac_year)
        _create_education_group_limited_daily_management_calendar(AcademicCalendar, ac_year)


def _create_education_group_preparation_calendar(academic_calendar_cls, targeted_academic_year):
    academic_calendar_cls.objects.update_or_create(
        reference=academic_calendar_type.EDUCATION_GROUP_EDITION,
        data_year=targeted_academic_year,
        defaults={
            "title": "Préparation des formations",
            "start_date": datetime.date(targeted_academic_year.year, 8, 15),
            "end_date": datetime.date(targeted_academic_year.year, 11, 20),
            "academic_year": targeted_academic_year
        }
    )


def _create_education_group_extended_daily_management_calendar(academic_calendar_cls, targeted_academic_year):
    academic_calendar_cls.objects.update_or_create(
        reference=academic_calendar_type.EDUCATION_GROUP_EXTENDED_DAILY_MANAGEMENT,
        data_year=targeted_academic_year,
        defaults={
            "title": "Gestion journalière étendue - catalogue",
            "start_date": datetime.date(targeted_academic_year.year - 6, 9, 15),
            "end_date": None,
            "academic_year": targeted_academic_year
        }
    )


def _create_education_group_limited_daily_management_calendar(academic_calendar_cls, targeted_academic_year):
    academic_calendar_cls.objects.update_or_create(
        reference=academic_calendar_type.EDUCATION_GROUP_LIMITED_DAILY_MANAGEMENT,
        data_year=targeted_academic_year,
        defaults={
            "title": "Gestion journalière limitée - catalogue",
            "start_date": datetime.date(targeted_academic_year.year - 2, 9, 15),
            "end_date": None,
            "academic_year": targeted_academic_year
        }
    )


class Migration(migrations.Migration):

    dependencies = [
        ('education_group', '0012_copy_title_english_from_egy_to_gy'),
    ]

    operations = [
        migrations.RunPython(create_education_group_academic_calendar, remove_education_group_academic_calendar),
    ]
