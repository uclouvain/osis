from backoffice.celery import app as celery_app
from education_group.calendar.education_group_preparation_calendar import EducationGroupPreparationCalendar


@celery_app.task
def run() -> dict:
    EducationGroupPreparationCalendar.ensure_consistency_until_n_plus_6()
    return {}
