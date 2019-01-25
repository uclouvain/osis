##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.db.models import Count, Q
from django.utils.translation import ugettext as _

from base.models.authorized_relationship import AuthorizedRelationship
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import AllTypes
from base.models.enums.link_type import LinkTypes
from base.models.exceptions import IncompatiblesTypesException, AuthorizedRelationshipNotRespectedException
from base.models.learning_unit_year import LearningUnitYear
from base.utils.cache import cache

# TODO Use meta name instead
LEARNING_UNIT_YEAR = 'learningunityear'
EDUCATION_GROUP_YEAR = 'educationgroupyear'
SELECT_CACHE_KEY = 'child_to_cache_id'


def select_education_group_year(education_group_year):
    return _set_selected_element_on_cache(education_group_year.pk, EDUCATION_GROUP_YEAR)


def select_learning_unit_year(learning_unit_year):
    return _set_selected_element_on_cache(learning_unit_year.pk, LEARNING_UNIT_YEAR)


def _set_selected_element_on_cache(id, modelname):
    data_to_cache = {'id': id, 'modelname': modelname}
    cache.set(SELECT_CACHE_KEY, data_to_cache, timeout=None)
    return True


def extract_child_from_cache(parent, selected_data):
    kwargs = {'parent': parent}
    if not selected_data:
        return {}

    if selected_data['modelname'] == LEARNING_UNIT_YEAR:
        luy = LearningUnitYear.objects.get(pk=selected_data['id'])
        if not parent.education_group_type.learning_unit_child_allowed:
            raise IncompatiblesTypesException(
                errors=_("You cannot attach \"%(child)s\" (type \"%(child_type)s\") "
                         "to \"%(parent)s\" (type \"%(parent_type)s\")") % {
                           'child': luy,
                           'child_type': _("Learning unit"),
                           'parent': parent,
                           'parent_type': parent.education_group_type,
                       }
            )
        kwargs['child_leaf'] = luy

    elif selected_data['modelname'] == EDUCATION_GROUP_YEAR:
        egy = EducationGroupYear.objects.get(pk=selected_data['id'])
        kwargs['child_branch'] = egy

    return kwargs


def is_max_child_reached(parent, child_education_group_type):
    try:
        auth_rel = parent.education_group_type.authorized_parent_type.get(child_type__name=child_education_group_type)
    except AuthorizedRelationship.DoesNotExist:
        return True

    try:
        education_group_type_count = compute_number_children_by_education_group_type(parent, None).\
            get(education_group_type__name=child_education_group_type)["count"]
    except EducationGroupYear.DoesNotExist:
        education_group_type_count = 0
    return auth_rel.max_count_authorized is not None and education_group_type_count >= auth_rel.max_count_authorized


def check_authorized_relationship(root, link, to_delete=False):
    auth_rels = root.education_group_type.authorized_parent_type.all().select_related("child_type")
    auth_rels_dict = {auth_rel.child_type.name: auth_rel for auth_rel in auth_rels}

    count_children_by_education_group_type_qs = compute_number_children_by_education_group_type(root, link, to_delete)
    count_children_dict = {
        record["education_group_type__name"]: record["count"] for record in count_children_by_education_group_type_qs
    }

    max_reached = []
    min_reached = []
    not_authorized = []
    for key, count in count_children_dict.items():
        if key not in auth_rels_dict:
            not_authorized.append(key)
        elif count < auth_rels_dict[key].min_count_authorized:
            min_reached.append(key)
        elif auth_rels_dict[key].max_count_authorized is not None \
                and count > auth_rels_dict[key].max_count_authorized:
            max_reached.append(key)

    # Check for technical group that would not be linked to root
    for key, auth_rel in auth_rels_dict.items():
        if key not in count_children_dict and auth_rel.min_count_authorized > 0:
            min_reached.append(key)

    if min_reached:
        raise AuthorizedRelationshipNotRespectedException(
            errors=_("The parent must have at least one child of type(s) \"%(types)s\".") % {
                "types": ', '.join(str(AllTypes.get_value(name)) for name in min_reached)
            }
        )
    elif max_reached:
        raise AuthorizedRelationshipNotRespectedException(
            errors=_("The number of children of type(s) \"%(child_types)s\" for \"%(parent)s\" "
                     "has already reached the limit.") % {
                       'child_types': ', '.join(str(AllTypes.get_value(name)) for name in max_reached),
                       'parent': root
                   }
        )
    elif not_authorized:
        raise AuthorizedRelationshipNotRespectedException(
                errors=_("You cannot attach \"%(child_types)s\" to \"%(parent)s\" (type \"%(parent_type)s\")") % {
                    'child_types': ', '.join(str(AllTypes.get_value(name)) for name in not_authorized),
                    'parent': root,
                    'parent_type': AllTypes.get_value(root.education_group_type.name),
                }
            )


def compute_number_children_by_education_group_type(root, link=None, to_delete=False):
    qs = EducationGroupYear.objects.filter(
        (Q(child_branch__parent=root) & Q(child_branch__link_type=None)) |
        (Q(child_branch__parent__child_branch__parent=root) &
         Q(child_branch__parent__child_branch__link_type=LinkTypes.REFERENCE.name))
    )
    if link:
        # Need to remove childrens in common between root and link to not false count
        records_to_remove_qs = EducationGroupYear.objects.filter(Q(pk=link.child_branch.pk) |
                                                                 Q(child_branch__parent=link.child_branch.pk))
        qs = qs.difference(records_to_remove_qs)

        link_children_qs = EducationGroupYear.objects.filter(pk=link.child_branch.pk)
        if link.link_type == LinkTypes.REFERENCE.name:
            link_children_qs = EducationGroupYear.objects.filter(child_branch__parent=link.child_branch.pk)

        if not to_delete:
            qs = qs.union(link_children_qs)

    # FIXME Because when applying the annotate on the union and intersection,
    #  it returns strange value for the count and education group type name
    pks = qs.values_list("pk", flat=True)
    qs = EducationGroupYear.objects.filter(pk__in=list(pks)). \
        values("education_group_type__name"). \
        order_by("education_group_type__name"). \
        annotate(count=Count("education_group_type__name"))
    return qs
