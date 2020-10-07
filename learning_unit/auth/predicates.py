from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rules import predicate

from attribution.models.tutor_application import TutorApplication
from base.business import event_perms
from base.models.enums import learning_container_year_types as container_types, learning_container_year_types
from base.models.enums.proposal_state import ProposalState
from base.models.enums.proposal_type import ProposalType
from base.models.proposal_learning_unit import ProposalLearningUnit
from osis_common.utils.models import get_object_or_none
from osis_role.cache import predicate_cache
from osis_role.errors import predicate_failed_msg

FACULTY_EDITABLE_CONTAINER_TYPES = (
    learning_container_year_types.COURSE,
    learning_container_year_types.DISSERTATION,
    learning_container_year_types.INTERNSHIP
)

PROPOSAL_CONSOLIDATION_ELIGIBLE_STATES = (ProposalState.ACCEPTED.name, ProposalState.REFUSED.name)


@predicate(bind=True)
@predicate_failed_msg(message=_("You can only modify a learning unit when your are linked to its requirement entity"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_user_attached_to_initial_requirement_entity(self, user, learning_unit_year=None):
    if learning_unit_year:
        initial_container_year = learning_unit_year.initial_data.get("learning_container_year")
        requirement_entity_id = initial_container_year.requirement_entity
        return _is_attached_to_entity(requirement_entity_id, self)
    return learning_unit_year


@predicate(bind=True)
@predicate_failed_msg(message=_("You can only modify a learning unit when your are linked to its requirement entity"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_user_attached_to_current_requirement_entity(self, user, learning_unit_year=None):
    if learning_unit_year:
        current_container_year = learning_unit_year.learning_container_year
        return current_container_year is not None and _is_attached_to_entity(
            current_container_year.requirement_entity_id, self
        )
    return learning_unit_year


def _is_attached_to_entity(requirement_entity, self):
    user_entity_ids = self.context['role_qs'].get_entities_ids()
    return requirement_entity in user_entity_ids


@predicate(bind=True)
@predicate_failed_msg(
    message="{}.  {}".format(
        _("You can't modify learning unit under year : %(year)d") %
        {"year": settings.YEAR_LIMIT_LUE_MODIFICATION + 1},
        _("Modifications should be made in EPC under year %(year)d") %
        {"year": settings.YEAR_LIMIT_LUE_MODIFICATION + 1},
    )
)
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_learning_unit_year_older_or_equals_than_limit_settings_year(self, user, learning_unit_year=None):
    if learning_unit_year:
        return learning_unit_year.academic_year.year > settings.YEAR_LIMIT_LUE_MODIFICATION
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("You cannot delete a learning unit which is prerequisite or has prerequisite(s)"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_learning_unit_year_not_prerequisite(self, user, learning_unit_year):
    if learning_unit_year:
        return not learning_unit_year.is_prerequisite()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("This learning unit has no application."))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def has_learning_unit_applications(self, user, learning_unit_year):
    if learning_unit_year:
        return TutorApplication.objects.filter(
            learning_container_year__learning_container=learning_unit_year.learning_container_year.learning_container
        ).exists()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("Learning unit type is not deletable"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_learning_unit_container_type_deletable(self, user, learning_unit_year):
    if learning_unit_year:
        container_type = learning_unit_year.learning_container_year.container_type
        is_full_course = container_type == container_types.COURSE and learning_unit_year.is_full()
        type_is_deletable = container_type not in [container_types.DISSERTATION, container_types.INTERNSHIP]
        return not is_full_course and type_is_deletable
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("This learning unit isn't eligible for modification because of it's type"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_learning_unit_container_type_editable(self, user, learning_unit_year):
    if learning_unit_year:
        container = learning_unit_year.learning_container_year
        return container and container.container_type in FACULTY_EDITABLE_CONTAINER_TYPES
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("This learning unit is not editable this period."))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_learning_unit_edition_period_open(self, user, learning_unit_year):
    if learning_unit_year:
        for role in self.context['role_qs']:
            return event_perms.generate_event_perm_learning_unit_edition(role.person, learning_unit_year).is_open()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("Modification or transformation proposal not allowed during this period."))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_proposal_date_edition_period_open(self, user, learning_unit_year):
    if learning_unit_year:
        for role in self.context['role_qs']:
            return event_perms.generate_event_perm_modification_transformation_proposal(
                role.person, learning_unit_year
            ).is_open()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("Date creation or modification of proposal not allowed during this period."))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_proposal_edition_period_open(self, user, learning_unit_year):
    if learning_unit_year:
        for role in self.context['role_qs']:
            return event_perms.generate_event_perm_creation_end_date_proposal(
                role.person, learning_unit_year
            ).is_open()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("Learning unit is not full"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_learning_unit_year_full(self, user, learning_unit_year):
    if learning_unit_year:
        return learning_unit_year.is_full()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("You can only edit co-graduation external learning units"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_external_learning_unit_with_cograduation(self, user, learning_unit_year):
    if learning_unit_year and hasattr(learning_unit_year, 'externallearningunityear'):
        return learning_unit_year.externallearningunityear.co_graduation
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("You cannot modify a learning unit of a previous year"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_learning_unit_year_not_in_past(self, user, learning_unit_year):
    if learning_unit_year:
        return not learning_unit_year.is_past()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("The learning unit is a partim"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_learning_unit_year_not_a_partim(self, user, learning_unit_year):
    if learning_unit_year:
        return not learning_unit_year.is_partim()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("The learning unit is not a partim"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_learning_unit_year_a_partim(self, user, learning_unit_year):
    if learning_unit_year:
        return learning_unit_year.is_partim()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("Not in proposal"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_proposal(self, user, learning_unit_year):
    if learning_unit_year:
        return ProposalLearningUnit.objects.filter(
            learning_unit_year__learning_unit=learning_unit_year.learning_unit,
            learning_unit_year__academic_year__year__lte=learning_unit_year.academic_year.year
        ).exists()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("You can't edit because the learning unit has proposal"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_not_proposal(self, user, learning_unit_year):
    if learning_unit_year:
        return not ProposalLearningUnit.objects.filter(
            learning_unit_year__learning_unit=learning_unit_year.learning_unit,
            learning_unit_year__academic_year__year__lte=learning_unit_year.academic_year.year
        ).exists()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("Person not in accordance with proposal state"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def has_faculty_proposal_state(self, user, learning_unit_year):
    if learning_unit_year:
        learning_unit_proposal = get_object_or_none(ProposalLearningUnit, learning_unit_year__id=learning_unit_year.pk)
        if learning_unit_proposal:
            return learning_unit_proposal.state == ProposalState.FACULTY.name
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("This learning unit has application"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_not_proposal_of_type_creation_with_applications(self, user, learning_unit_year):
    if learning_unit_year:
        proposal = get_object_or_none(ProposalLearningUnit, learning_unit_year__id=learning_unit_year.pk)
        if proposal:
            return proposal.type != ProposalType.CREATION.name or not TutorApplication.objects.filter(
                learning_container_year=proposal.learning_unit_year.learning_container_year
            ).exists()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("This learning unit has application"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_not_proposal_of_type_suppression_with_applications(self, user, learning_unit_year):
    if learning_unit_year:
        proposal = get_object_or_none(ProposalLearningUnit, learning_unit_year__id=learning_unit_year.pk)
        if proposal:
            return proposal.type != ProposalType.SUPPRESSION.name or not TutorApplication.objects.filter(
                learning_container_year=proposal.learning_unit_year.learning_container_year
            ).exists()
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("This learning unit has application this year"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def has_learning_unit_no_application_this_year(self, user, learning_unit_year):
    if learning_unit_year:
        learning_container_year = learning_unit_year.learning_container_year
        return not TutorApplication.objects.filter(learning_container_year=learning_container_year).exists()


@predicate(bind=True)
@predicate_failed_msg(message=_("This learning unit has application"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def has_learning_unit_no_application_all_year(self, user, learning_unit_year):
    if learning_unit_year:
        learning_container = learning_unit_year.learning_container_year.learning_container
        return not TutorApplication.objects.filter(
            learning_container_year__learning_container=learning_container
        ).exists()


@predicate(bind=True)
@predicate_failed_msg(message=_("Proposal not in eligible state for consolidation"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_proposal_in_state_to_be_consolidated(self, user, learning_unit_year):
    if learning_unit_year:
        learning_unit_proposal = get_object_or_none(ProposalLearningUnit, learning_unit_year__id=learning_unit_year.pk)
        if learning_unit_proposal:
            return learning_unit_proposal.state in PROPOSAL_CONSOLIDATION_ELIGIBLE_STATES
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("Proposal is of modification type"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_not_modification_proposal_type(self, user, learning_unit_year):
    if learning_unit_year:
        learning_unit_proposal = get_object_or_none(ProposalLearningUnit, learning_unit_year__id=learning_unit_year.pk)
        if learning_unit_proposal:
            return learning_unit_proposal.type != ProposalType.MODIFICATION.name
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("Learning unit type is not allowed for attributions"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_learning_unit_type_allowed_for_attributions(self, user, learning_unit_year):
    if learning_unit_year:
        container_type = learning_unit_year.learning_container_year.container_type
        return container_type in learning_container_year_types.TYPE_ALLOWED_FOR_ATTRIBUTIONS
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("Learning unit has no container"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_learning_unit_with_container(self, user, learning_unit_year):
    if learning_unit_year:
        return learning_unit_year.learning_container_year
    return None
