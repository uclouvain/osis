from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rules import predicate

from attribution.models.tutor_application import TutorApplication
from base.business.event_perms import EventPermLearningUnitCentralManagerEdition
from base.models.enums import learning_container_year_types as container_types
from base.models.proposal_learning_unit import ProposalLearningUnit
from osis_role.errors import predicate_failed_msg


@predicate(bind=True)
@predicate_failed_msg(message=_("You can only modify a learning unit when your are linked to its requirement entity"))
def is_user_attached_to_management_entity(self, user, learning_unit_year=None):
    if learning_unit_year:
        user_entity_ids = self.context['role_qs'].get_entities_ids()
        return learning_unit_year.management_entity_id in user_entity_ids
    return learning_unit_year


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
@predicate_failed_msg(message=_("You can't edit because the learning unit has proposal"))
def is_not_proposal(self, user, learning_unit_year):
    if learning_unit_year:
        return not ProposalLearningUnit.objects.filter(
            learning_unit_year__learning_unit=learning_unit_year.learning_unit,
            learning_unit_year__academic_year__year__lte=learning_unit_year.academic_year.year
        ).exists()
    return None
