from assessments.calendar.scores_exam_diffusion_calendar import ScoreExamDiffusionCalendar
from backoffice.celery import app as celery_app


@celery_app.task
def run() -> dict:
    ScoreExamDiffusionCalendar.ensure_consistency_until_n_plus_6()
    return {}
