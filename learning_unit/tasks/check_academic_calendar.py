from backoffice.celery import app as celery_app

from learning_unit.calendar.learning_unit_extended_proposal_management import \
    LearningUnitExtendedProposalManagementCalendar
from learning_unit.calendar.learning_unit_limited_proposal_management import \
    LearningUnitLimitedProposalManagementCalendar


@celery_app.task
def run() -> dict:
    LearningUnitExtendedProposalManagementCalendar.ensure_consistency_until_n_plus_6()
    LearningUnitLimitedProposalManagementCalendar.ensure_consistency_until_n_plus_6()
    return {}
