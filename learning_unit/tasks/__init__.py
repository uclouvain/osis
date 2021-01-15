from celery.schedules import crontab

from backoffice.celery import app as celery_app
from . import check_academic_calendar

celery_app.conf.beat_schedule.update({
    '|Learning Unit| Check academic calendar': {
        'task': 'learning_unit.tasks.check_academic_calendar.run',
        'schedule': crontab(minute=0, hour=0, day_of_month='*', month_of_year='*', day_of_week=0)
    },
})