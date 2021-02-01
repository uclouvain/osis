from assessments.calendar.scores_diffusion_calendar import ScoresDiffusionCalendar
from backoffice.celery import app as celery_app


@celery_app.task
def run() -> dict:
    ScoresDiffusionCalendar.ensure_consistency_until_n_plus_6()
    return {}
