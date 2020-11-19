from typing import Union

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _, pgettext
from rules import predicate

from base.business.event_perms import EventPermEducationGroupEdition
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_categories import Categories
from base.models.enums.education_group_types import TrainingType
from education_group.auth.scope import Scope
from education_group.models.group_year import GroupYear
from osis_common.ddd import interface
from osis_role.errors import predicate_failed_msg, set_permission_error, get_permission_error
from osis_role.cache import predicate_cache
from program_management.ddd.domain import exception
from program_management.ddd.domain.service import identity_search
from program_management.ddd.repositories import load_tree_version, \
    program_tree_version as program_tree_version_repository
from program_management.models.element import Element


@predicate(bind=True)
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def are_all_training_versions_removable(self, user, group_year):
    groups = group_year.group.groupyear_set.all().select_related(
        'education_group_type', 'management_entity', 'academic_year'
    )
    return _are_all_removable(self, user, groups, 'program_management.delete_training_version')


@predicate(bind=True)
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def are_all_mini_training_versions_removable(self, user, group_year):
    groups = group_year.group.groupyear_set.all().select_related(
        'education_group_type', 'management_entity', 'academic_year'
    )
    return _are_all_removable(self, user, groups, 'program_management.delete_minitraining_version')


@predicate(bind=True)
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def are_all_trainings_removable(self, user, training_root):
    training_roots = training_root.group.groupyear_set.all().select_related(
        'education_group_type', 'management_entity', 'academic_year'
    )
    return _are_all_removable(self, user, training_roots, 'base.delete_training')


@predicate(bind=True)
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def are_all_minitrainings_removable(self, user, minitraining_root):
    minitraining_roots = minitraining_root.group.groupyear_set.all().select_related(
        'education_group_type',
        'management_entity',
        'academic_year'
    )
    return _are_all_removable(self, user, minitraining_roots, 'base.delete_minitraining')


@predicate(bind=True)
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def are_all_groups_removable(self, user, group_year):
    groups = group_year.group.groupyear_set.all().select_related(
        'education_group_type', 'management_entity', 'academic_year'
    )
    return _are_all_removable(self, user, groups, 'base.delete_group')


def _are_all_removable(self, user, objects, perm):
    # use shortcut break : at least one should not have perm to trigger error
    result = all(
        user.has_perm(perm, object)
        for object in objects.order_by('academic_year__year')
    )
    # transfers last perm error message
    message = get_permission_error(user, perm)
    set_permission_error(user, self.context['perm_name'], message)
    return result


@predicate(bind=True)
@predicate_failed_msg(
    message=pgettext("male", "The user does not have permission to create a %(category)s.") %
    {"category": Categories.GROUP.value}
)
def is_not_orphan_group(self, user, education_group_year=None):
    return education_group_year is not None


# FIXME: Move to business logic because it's not a predicate (found in MinimumEditableYearValidator)
@predicate(bind=True)
@predicate_failed_msg(
    message=_("You cannot change/delete a education group existing before %(limit_year)s") %
    {"limit_year": settings.YEAR_LIMIT_EDG_MODIFICATION}
)
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_education_group_year_older_or_equals_than_limit_settings_year(
        self,
        user: User,
        obj: Union[EducationGroupYear, GroupYear] = None
):
    if obj:
        return obj.academic_year.year >= settings.YEAR_LIMIT_EDG_MODIFICATION
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("The user is not allowed to create/modify this type of education group"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_education_group_type_authorized_according_to_user_scope(
        self,
        user: User,
        obj: Union[EducationGroupYear, GroupYear] = None
):
    if obj:
        return any(
            obj.education_group_type.name in role.get_allowed_education_group_types()
            for role in self.context['role_qs']
            if obj.management_entity_id in self.context['role_qs'].filter(pk=role.pk).get_entities_ids()
        )
    return None


@predicate(bind=True)
@predicate_failed_msg(message=_("The user is not attached to the management entity"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_user_attached_to_management_entity(
        self,
        user: User,
        obj: Union[EducationGroupYear, GroupYear] = None
):
    if obj:
        user_entity_ids = self.context['role_qs'].get_entities_ids()
        return obj.management_entity_id in user_entity_ids
    return obj


# FIXME: Move to business logic because it's not a predicate
@predicate(bind=True)
@predicate_failed_msg(message=_("You must create the version of the concerned training and then attach that version"
                                " inside this version"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_element_only_inside_standard_program(
        self,
        user: User,
        education_group_year: Union[EducationGroupYear, GroupYear] = None
):
    if isinstance(education_group_year, GroupYear):
        element_id = Element.objects.get(group_year=education_group_year).id
        try:
            node_identity = identity_search.NodeIdentitySearch.get_from_element_id(element_id)
            tree_version_identity = identity_search.ProgramTreeVersionIdentitySearch(
            ).get_from_node_identity(
                node_identity
            )
            tree_version = tree_version_identity and program_tree_version_repository.ProgramTreeVersionRepository(
            ).get(tree_version_identity)
            if tree_version and not tree_version.is_standard_version:
                return False
        except (interface.BusinessException, exception.ProgramTreeVersionNotFoundException):
            pass
        tree_versions = load_tree_version.load_tree_versions_from_children([element_id])
        return all((version.is_standard_version for version in tree_versions))
    return education_group_year


@predicate(bind=True)
@predicate_failed_msg(message=EventPermEducationGroupEdition.error_msg)
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_program_edition_period_open(self, user, group_year: 'GroupYear' = None):
    return EventPermEducationGroupEdition(obj=group_year, raise_exception=False).is_open()


@predicate(bind=True)
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_continuing_education_group_year(self, user, obj: Union['GroupYear', 'EducationGroupYear'] = None):
    return obj and obj.education_group_type.name in TrainingType.continuing_education_types()


@predicate(bind=True)
@predicate_failed_msg(message=_("The scope of the user is limited and prevents this action to be performed"))
@predicate_cache(cache_key_fn=lambda obj: getattr(obj, 'pk', None))
def is_user_linked_to_all_scopes_of_management_entity(self, user, obj: Union['GroupYear', 'EducationGroupYear']):
    if obj:
        user_scopes = {
            entity_id: scope for role in self.context['role_qs']
            for scope in role.scopes if hasattr(role, 'scopes')
            for entity_id in self.context['role_qs'].filter(pk=role.pk).get_entities_ids()
        }
        return user_scopes.get(obj.management_entity_id) == Scope.ALL.value
    return None
