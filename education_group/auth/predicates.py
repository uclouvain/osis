from django.conf import settings
from django.utils.translation import gettext_lazy as _, pgettext
from rules import predicate

from base.business.event_perms import EventPermEducationGroupEdition
from base.models.education_group_type import EducationGroupType
from base.models.enums.education_group_categories import Categories
from base.models.enums.education_group_types import GroupType
from education_group.auth.scope import Scope
from osis_role import errors
from osis_role.errors import predicate_failed_msg


@predicate(bind=True)
def are_all_education_group_years_removable(self, user, education_group):
    education_group_years = education_group.educationgroupyear_set.all()
    return all(
        user.has_perm('base.delete_educationgroup', education_group_year)
        for education_group_year in education_group_years
    )


@predicate(bind=True)
@predicate_failed_msg(
    message=pgettext("male", "The user does not have permission to create a %(category)s.") %
    {"category": Categories.GROUP.value}
)
def is_not_orphan_group(self, user, education_group_year=None):
    return education_group_year is not None


@predicate(bind=True)
@predicate_failed_msg(
    message=_("You cannot change a education group before %(limit_year)s") %
    {"limit_year": settings.YEAR_LIMIT_EDG_MODIFICATION}
)
def is_education_group_year_older_or_equals_than_limit_settings_year(self, user, education_group_year=None):
    if education_group_year:
        return education_group_year.academic_year.year >= settings.YEAR_LIMIT_EDG_MODIFICATION
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("The user is not allowed to create/modify this type of education group"))
def is_education_group_type_authorized_according_to_user_scope(self, user, education_group_year=None):
    if education_group_year:
        return any(
            education_group_year.education_group_type.name in role_row.get_allowed_education_group_types()
            for role_row in self.context['role_qs'] if role_row.entity == education_group_year.management_entity
        )
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("The user is not attached to the management entity"))
def is_user_attached_to_management_entity(self, user, education_group_year=None):
    if education_group_year:
        user_entity_ids = self.context['role_qs'].get_entities_ids()
        return education_group_year.management_entity_id in user_entity_ids
    return education_group_year


@predicate(bind=True)
@predicate_failed_msg(message=EventPermEducationGroupEdition.error_msg)
def is_program_edition_period_open(self, user, education_group_year=None):
    return EventPermEducationGroupEdition(obj=education_group_year, raise_exception=False).is_open()


@predicate(bind=True)
def is_continuing_education_group_year(self, user, education_group_year=None):
    return education_group_year and education_group_year.is_continuing_education_education_group_year


@predicate(bind=True)
def is_maximum_child_not_reached_for_group_category(self, user, education_group_year=None):
    if education_group_year:
        return _is_maximum_child_not_reached_for_category(self, user, education_group_year, Categories.GROUP.name)
    return None


@predicate(bind=True)
def is_maximum_child_not_reached_for_training_category(self, user, education_group_year=None):
    if education_group_year:
        return _is_maximum_child_not_reached_for_category(self, user, education_group_year, Categories.TRAINING.name)
    return None


@predicate(bind=True)
def is_maximum_child_not_reached_for_mini_training_category(self, user, education_group_year=None):
    if education_group_year:
        return _is_maximum_child_not_reached_for_category(self, user, education_group_year,
                                                          Categories.MINI_TRAINING.name)
    return None


def _is_maximum_child_not_reached_for_category(self, user, education_group_year, category):
    result = EducationGroupType.objects.filter(
        category=category,
        authorized_child_type__parent_type__educationgroupyear=education_group_year
    ).exists()

    if not result:
        message = pgettext(
            "female" if education_group_year.education_group_type.category in [
                Categories.TRAINING,
                Categories.MINI_TRAINING
            ] else "male",
            "No type of %(child_category)s can be created as child of %(category)s of type %(type)s"
        ) % {
            "child_category": Categories[category].name,
            "category": education_group_year.education_group_type.get_category_display(),
            "type": education_group_year.education_group_type.get_name_display(),
        }
        errors.set_permission_error(user, self.context['perm_name'], message)
    return result


@predicate(bind=True)
@predicate_failed_msg(message=_("The scope of the user is limited and prevents this action to be performed"))
def is_user_linked_to_all_scopes_of_management_entity(self, user, education_group_year):
    if education_group_year:
        user_scopes = {
            role.entity: scope for role in self.context['role_qs'] for scope in role.scopes if hasattr(role, 'scopes')
        }
        return user_scopes.get(education_group_year.management_entity) == Scope.ALL.value
    return None


@predicate(bind=True)
@predicate_failed_msg(
    message=_("You cannot modify content for %(education_group_types)s") % {
        "education_group_types": ", ".join(
            [str(GroupType.MAJOR_LIST_CHOICE.value), str(GroupType.MINOR_LIST_CHOICE.value)])
        }
)
def is_child_education_group_type_not_minor_or_major(self, user, egy=None):
    if egy:
        excluded_types = (GroupType.MAJOR_LIST_CHOICE.name, GroupType.MINOR_LIST_CHOICE.name)
        return egy.education_group_type.name not in excluded_types and not egy.is_minor
    return None
