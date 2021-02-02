from assessments.calendar.scores_diffusion_calendar import ScoresDiffusionCalendar
from assessments.calendar.scores_exam_submission_calendar import ScoresExamSubmissionCalendar
from backoffice.celery import app as celery_app


@celery_app.task
def run() -> dict:
    ScoresDiffusionCalendar.ensure_consistency_until_n_plus_6()
    ScoresExamSubmissionCalendar.ensure_consistency_until_n_plus_6()
    return {}
