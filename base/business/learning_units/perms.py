##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

from attribution.business.perms import _is_tutor_attributed_to_the_learning_unit
from base.business.institution import find_summary_course_submission_dates_for_entity_version
from base.models import proposal_learning_unit, tutor, entity_calendar
from base.models.entity import Entity
from base.models.entity_version import EntityVersion
from base.models.enums import learning_container_year_types, academic_calendar_type
from base.models.enums.proposal_state import ProposalState
from base.models.learning_unit_year import LearningUnitYear
from osis_common.utils.datetime import get_tzinfo, convert_date_to_datetime
from osis_common.utils.perms import BasePerm

FACULTY_UPDATABLE_CONTAINER_TYPES = (
    learning_container_year_types.COURSE,
    learning_container_year_types.DISSERTATION,
    learning_container_year_types.INTERNSHIP
)

PROPOSAL_CONSOLIDATION_ELIGIBLE_STATES = (ProposalState.ACCEPTED.name, ProposalState.REFUSED.name)

MSG_PERSON_NOT_IN_ACCORDANCE_WITH_PROPOSAL_STATE = _("Person not in accordance with proposal state")
MSG_PROPOSAL_NOT_IN_CONSOLIDATION_ELIGIBLE_STATES = _("Proposal not in eligible state for consolidation")
MSG_CAN_DELETE_ACCORDING_TO_TYPE = _("Can delete according to the type of the learning unit")


def learning_unit_year_permissions(learning_unit_year, person):
    return {
        'can_propose': person.user.has_perm('base.can_propose_learningunit', learning_unit_year),
        'can_edit_date': person.user.has_perm('base.can_edit_learningunit_date', learning_unit_year),
        'can_edit': person.user.has_perm('base.can_edit_learningunit', learning_unit_year),
        'can_delete': person.user.has_perm('base.can_delete_learningunit', learning_unit_year),
    }


def learning_unit_proposal_permissions(proposal, person, current_learning_unit_year):
    permissions = {
        'can_cancel_proposal': False,
        'can_edit_learning_unit_proposal': False,
        'can_consolidate_proposal': False
    }
    if not proposal or proposal.learning_unit_year != current_learning_unit_year:
        return permissions
    luy = proposal.learning_unit_year
    permissions['can_cancel_proposal'] = person.user.has_perm('base.can_cancel_proposal', luy)
    permissions['can_edit_learning_unit_proposal'] = person.user.has_perm('base.can_edit_learning_unit_proposal', luy)
    permissions['can_consolidate_proposal'] = person.user.has_perm('base.can_consolidate_learningunit_proposal', luy)
    return permissions


# should be migrated with tutor role creation
def is_eligible_to_update_learning_unit_pedagogy(learning_unit_year, person):
    """
    Permission to edit learning unit pedagogy needs many conditions:
        - The person must have the permission can_edit_learning_pedagogy
        - The person must be link to requirement entity
        - The person can be a faculty or a central manager
        - The person can be a tutor:
            - The learning unit must have its flag summary_locked to false
            - The person must have an attribution for the learning unit year
            - The attribution must have its flag summary responsible to true.

    :param learning_unit_year: LearningUnitYear
    :param person: Person
    :return: bool
    """
    if person.user.has_perm('base.can_edit_learningunit_pedagogy', learning_unit_year):
        return True
    # Case Tutor: We need to check if today is between submission date
    if tutor.is_tutor(person.user):
        return can_user_edit_educational_information(
            user=person.user,
            learning_unit_year_id=learning_unit_year.id
        ).is_valid()

    return False


def is_eligible_to_update_learning_unit_pedagogy_force_majeure_section(learning_unit_year, person):
    if not person.user.has_perm('base.can_edit_learningunit_pedagogy'):
        return False
    if is_year_editable(learning_unit_year, raise_exception=False):
        # Case faculty/central: We need to check if user is linked to entity
        if person.is_faculty_manager or person.is_central_manager:
            return person.is_linked_to_entity_in_charge_of_learning_unit_year(learning_unit_year)

        # Case Tutor: We need to check if today is between submission date of force majeure section
        if tutor.is_tutor(person.user):
            return can_user_edit_educational_information_force_majeure(
                user=person.user,
                learning_unit_year_id=learning_unit_year.id
            ).is_valid()
    return False


def _is_tutor_summary_responsible_of_learning_unit_year(*, user, learning_unit_year_id, **kwargs):
    if not _is_tutor_attributed_to_the_learning_unit(user, learning_unit_year_id):
        raise PermissionDenied(_("You are not attributed to this learning unit."))


def _is_learning_unit_year_summary_editable(*, learning_unit_year_id, **kwargs):
    if isinstance(learning_unit_year_id, LearningUnitYear):
        value = True
    else:
        value = LearningUnitYear.objects.filter(pk=learning_unit_year_id, summary_locked=False).exists()

    if not value:
        raise PermissionDenied(_("The learning unit's description fiche is not editable."))


def _is_calendar_opened_to_edit_educational_information(*, learning_unit_year_id, **kwargs):
    submission_dates = find_educational_information_submission_dates_of_learning_unit_year(learning_unit_year_id)
    permission_denied_msg = _("Not in period to edit description fiche.")
    if not submission_dates:
        raise PermissionDenied(permission_denied_msg)

    now = datetime.datetime.now(tz=get_tzinfo())
    value = convert_date_to_datetime(submission_dates["start_date"]) <= now <= \
            convert_date_to_datetime(submission_dates["end_date"])
    if not value:
        raise PermissionDenied(permission_denied_msg)


def find_educational_information_submission_dates_of_learning_unit_year(learning_unit_year_id):
    requirement_entity_version = find_last_requirement_entity_version(
        learning_unit_year_id=learning_unit_year_id,
    )
    if requirement_entity_version is None:
        return {}

    return find_summary_course_submission_dates_for_entity_version(
        entity_version=requirement_entity_version,
        ac_year=LearningUnitYear.objects.get(pk=learning_unit_year_id).academic_year
    )


def _is_calendar_opened_to_edit_educational_information_force_majeure_section(*, learning_unit_year_id, **kwargs):
    submission_dates = find_educational_information_force_majeure_submission_dates_of_learning_unit_year(
        learning_unit_year_id
    )
    permission_denied_msg = _("Not in period to edit force majeure section.")
    if not submission_dates:
        raise PermissionDenied(permission_denied_msg)

    now = datetime.datetime.now(tz=get_tzinfo())
    value = convert_date_to_datetime(submission_dates["start_date"]) <= now <= \
            convert_date_to_datetime(submission_dates["end_date"])
    if not value:
        raise PermissionDenied(permission_denied_msg)


def find_educational_information_force_majeure_submission_dates_of_learning_unit_year(learning_unit_year_id):
    requirement_entity_version = find_last_requirement_entity_version(
        learning_unit_year_id=learning_unit_year_id,
    )
    if requirement_entity_version is None:
        return {}

    return entity_calendar.find_interval_dates_for_entity(
        ac_year=LearningUnitYear.objects.get(pk=learning_unit_year_id).academic_year,
        reference=academic_calendar_type.SUMMARY_COURSE_SUBMISSION_FORCE_MAJEURE,
        entity=requirement_entity_version.entity
    )


def find_last_requirement_entity_version(learning_unit_year_id):
    now = datetime.datetime.now(get_tzinfo())
    # TODO :: merge code below to get only 1 hit on database
    requirement_entity_id = LearningUnitYear.objects.filter(
        pk=learning_unit_year_id
    ).select_related(
        'learning_container_year'
    ).only(
        'learning_container_year'
    ).get().learning_container_year.requirement_entity_id
    try:
        return EntityVersion.objects.current(now).filter(entity=requirement_entity_id).get()
    except EntityVersion.DoesNotExist:
        return None


class can_user_edit_educational_information(BasePerm):
    predicates = (
        _is_tutor_summary_responsible_of_learning_unit_year,
        _is_learning_unit_year_summary_editable,
        _is_calendar_opened_to_edit_educational_information
    )


def is_year_editable(learning_unit_year, raise_exception):
    result = learning_unit_year.academic_year.year > settings.YEAR_LIMIT_LUE_MODIFICATION
    msg = "{}.  {}".format(
        _("You can't modify learning unit under year : %(year)d") %
        {"year": settings.YEAR_LIMIT_LUE_MODIFICATION + 1},
        _("Modifications should be made in EPC for year %(year)d") %
        {"year": learning_unit_year.academic_year.year},
    )
    can_raise_exception(raise_exception,
                        result,
                        msg)
    return result


def can_raise_exception(raise_exception, result, msg):
    if raise_exception and not result:
        raise PermissionDenied(msg)