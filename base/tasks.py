from celery.schedules import crontab

from backoffice.celery import app as celery_app
from base.business.education_groups.automatic_postponement import EducationGroupAutomaticPostponement
from base.business.learning_units.automatic_postponement import LearningUnitAutomaticPostponement

celery_app.conf.beat_schedule.update({
    'Extend learning units': {
        'task': 'base.tasks.extend_learning_units',
        'schedule': crontab(minute=0, hour=0, day_of_month=15, month_of_year=7)
    },
})


@celery_app.task
def extend_learning_units():
    process = LearningUnitAutomaticPostponement()
    process.postpone()
    return process.serialize_postponement_results()


celery_app.conf.beat_schedule.update({
    'Extend education groups': {
        'task': 'base.tasks.extend_education_groups',
        'schedule': crontab(minute=0, hour=2, day_of_month=15, month_of_year=7)
    },
})


@celery_app.task
def extend_education_groups():
    process = EducationGroupAutomaticPostponement()
    process.postpone()
    return process.serialize_postponement_results()
