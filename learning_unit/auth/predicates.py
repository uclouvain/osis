from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rules import predicate

from attribution.models.tutor_application import TutorApplication
from base.business.event_perms import EventPermLearningUnitCentralManagerEdition
from base.models.enums import learning_container_year_types as container_types, learning_container_year_types
from base.models.enums.proposal_state import ProposalState
from base.models.enums.proposal_type import ProposalType
from base.models.proposal_learning_unit import ProposalLearningUnit
from osis_common.utils.models import get_object_or_none
from osis_role.errors import predicate_failed_msg

FACULTY_EDITABLE_CONTAINER_TYPES = (
    learning_container_year_types.COURSE,
    learning_container_year_types.DISSERTATION,
    learning_container_year_types.INTERNSHIP
)


@predicate(bind=True)
@predicate_failed_msg(message=_("You can only modify a learning unit when your are linked to its requirement entity"))
def is_user_attached_to_initial_management_entity(self, user, learning_unit_year=None):
    if learning_unit_year:
        initial_container_year = learning_unit_year.initial_data.get("learning_container_year")
        requirement_entity_id = initial_container_year.get('requirement_entity')
        return _is_attached_to_entity(requirement_entity_id, self)
    return learning_unit_year


@predicate(bind=True)
@predicate_failed_msg(message=_("You can only modify a learning unit when your are linked to its requirement entity"))
def is_user_attached_to_current_management_entity(self, user, learning_unit_year=None):
    if learning_unit_year:
        return _is_attached_to_entity(learning_unit_year.management_entity_id, self)
    return learning_unit_year


def _is_attached_to_entity(requirement_entity, self):
    user_entity_ids = self.context['role_qs'].get_entities_ids()
    return requirement_entity in user_entity_ids


@predicate(bind=True)
@predicate_failed_msg(
    message=_("You cannot change/delete a learning unit existing before %(limit_year)s") %
    {"limit_year": settings.YEAR_LIMIT_LUE_MODIFICATION}
)
def is_learning_unit_year_older_or_equals_than_limit_settings_year(self, user, learning_unit_year=None):
    if learning_unit_year:
        return learning_unit_year.academic_year.year >= settings.YEAR_LIMIT_LUE_MODIFICATION
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("You cannot delete a learning unit which is prerequisite or has prerequisite(s)"))
def is_learning_unit_year_prerequisite(self, user, learning_unit_year):
    if learning_unit_year:
        return learning_unit_year.is_prerequisite()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("This learning unit has application."))
def has_learning_unit_applications(self, user, learning_unit_year):
    if learning_unit_year:
        return TutorApplication.objects.filter(
            learning_container_year__learning_container=learning_unit_year.learning_container_year.learning_container
        ).exists()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("Learning unit type is not deletable"))
def is_learning_unit_container_type_deletable(self, user, learning_unit_year):
    if learning_unit_year:
        container_type = learning_unit_year.learning_container_year.container_type
        is_full_course = container_type == container_types.COURSE and learning_unit_year.is_full()
        type_is_deletable = container_type not in [container_types.DISSERTATION, container_types.INTERNSHIP]
        return not is_full_course and type_is_deletable
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("This learning unit isn't eligible for modification because of it's type"))
def is_learning_unit_container_type_editable(self, user, learning_unit_year):
    if learning_unit_year:
        container = learning_unit_year.learning_container_year
        return container and container.container_type in FACULTY_EDITABLE_CONTAINER_TYPES
    return None


@predicate(bind=True)
@predicate_failed_msg(message=EventPermLearningUnitCentralManagerEdition.error_msg)
def is_edition_period_open(self, user, learning_unit_year):
    if learning_unit_year:
        # TODO : make predicate independent from role
        EventPermLearningUnitCentralManagerEdition(obj=learning_unit_year).is_open()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("Learning unit is not full"))
def is_learning_unit_year_full(self, user, learning_unit_year):
    if learning_unit_year:
        return learning_unit_year.is_full()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("You can only edit co-graduation external learning units"))
def is_external_learning_unit_cograduation(self, user, learning_unit_year):
    if learning_unit_year:
        return hasattr(learning_unit_year, 'externallearningunityear') or \
             learning_unit_year.externallearningunityear.co_graduation
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("You cannot modify a learning unit of a previous year"))
def is_learning_unit_year_not_in_past(self, user, learning_unit_year):
    if learning_unit_year:
        return learning_unit_year.is_past()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("The learning unit is a partim"))
def is_learning_unit_year_not_a_partim(self, user, learning_unit_year):
    if learning_unit_year:
        return learning_unit_year.is_partim()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("You can't edit because the learning unit has proposal"))
def is_not_proposal(self, user, learning_unit_year):
    if learning_unit_year:
        return not ProposalLearningUnit.objects.filter(
            learning_unit_year__learning_unit=learning_unit_year.learning_unit,
            learning_unit_year__academic_year__year__lte=learning_unit_year.academic_year.year
        ).exists()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("Person not in accordance with proposal state"))
def has_faculty_proposal_state(self, user, learning_unit_year):
    if learning_unit_year:
        learning_unit_proposal = get_object_or_none(ProposalLearningUnit, learning_unit_year__id=learning_unit_year.pk)
        if learning_unit_proposal:
            return learning_unit_proposal.state == ProposalState.FACULTY.name
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("This learning unit has application"))
def is_not_proposal_of_type_creation_with_applications(self, user, learning_unit_year):
    if learning_unit_year:
        proposal = get_object_or_none(ProposalLearningUnit, learning_unit_year__id=learning_unit_year.pk)
        if proposal:
            return proposal.type != ProposalType.CREATION.name or not TutorApplication.objects.filter(
                learning_container_year=proposal.learning_unit_year.learning_container_year
            ).exists()
    return None

