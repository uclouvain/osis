from backoffice.celery import app as celery_app
from education_group.calendar.education_group_edition_process_calendar import EducationGroupEditionCalendar


@celery_app.task
def run() -> dict:
    EducationGroupEditionCalendar().ensure_consistency_until_n_plus_6()
    return {}
