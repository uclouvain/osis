from celery.schedules import crontab

from backoffice.celery import app as celery_app
from base.business.education_groups.automatic_postponement import EducationGroupAutomaticPostponementToN6, \
    ReddotEducationGroupAutomaticPostponement
from base.business.learning_units.automatic_postponement import LearningUnitAutomaticPostponementToN6

celery_app.conf.beat_schedule.update({
    'Extend learning units': {
        'task': 'base.tasks.extend_learning_units',
        'schedule': crontab(minute=0, hour=0, day_of_month=15, month_of_year=7)
    },
})


@celery_app.task
def extend_learning_units():
    process = LearningUnitAutomaticPostponementToN6()
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
    process = EducationGroupAutomaticPostponementToN6()
    process.postpone()
    return process.serialize_postponement_results()



celery_app.conf.beat_schedule.update({
    'Extend reddot data': {
        'task': 'base.tasks.exytend_reddot_data',
        'schedule': crontab(minute=0, hour=1, day_of_month=1, month_of_year=7)
    },
})


@celery_app.task
def exytend_reddot_data():
    process = ReddotEducationGroupAutomaticPostponement()
    process.postpone()
    return process.serialize_postponement_results()


