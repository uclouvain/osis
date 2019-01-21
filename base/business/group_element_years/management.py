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
from collections import defaultdict

from django.db.models import Count, Q, F
from django.utils.translation import ugettext as _

from base.models.authorized_relationship import AuthorizedRelationship
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import AllTypes
from base.models.enums.link_type import LinkTypes
from base.models.exceptions import IncompatiblesTypesException, MaxChildrenReachedException, MinChildrenReachedException
from base.models.group_element_year import GroupElementYear
from base.models.learning_unit_year import LearningUnitYear
from base.models.utils.utils import get_verbose_field_value
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
    number_children_by_education_group_type = compute_number_children_by_education_group_type(parent, None, None)
    return number_children_by_education_group_type.get(child_education_group_type, 0) > auth_rel.max_count_authorized


def check_min_max_child_reached(parent, old_link, new_link):
    auth_rels = parent.education_group_type.authorized_parent_type.all()
    auth_rels_dict = {auth_rel.child_type.name: (auth_rel.min_count_authorized, auth_rel.max_count_authorized)
                      for auth_rel in auth_rels}
    number_children_by_education_group_type = compute_number_children_by_education_group_type(parent, old_link,
                                                                                              new_link)

    for education_group_type_name, number_children in number_children_by_education_group_type.items():
        if education_group_type_name not in auth_rels_dict:
            raise AuthorizedRelationship.DoesNotExist(
                _("You cannot attach a \"%(child_type)s\" to \"%(parent)s\" (type \"%(parent_type)s\")") % {
                    'child_type': AllTypes.get_value(education_group_type_name),
                    'parent': parent,
                    'parent_type': AllTypes.get_value(parent.education_group_type.name),
                }
            )

        min_authorized, max_authorized = auth_rels_dict[education_group_type_name]

        if number_children < min_authorized:
            raise MinChildrenReachedException(
                errors=_("The parent must have at least one child of type \"%(type)s\".") % {
                        "type": AllTypes.get_value(education_group_type_name)
                    }
            )

        if max_authorized is not None and number_children > max_authorized:
            raise MaxChildrenReachedException(
                errors=_("The number of children of type \"%(child_type)s\" for \"%(parent)s\" "
                         "has already reached the limit.") % {
                           'child_type': AllTypes.get_value(education_group_type_name),
                           'parent': parent
                       }
            )


def compute_number_children_by_education_group_type(egy, old_link, new_link):
    """
    Works by counting the number of children by education group type of the education group year egy.
    The old link is the link that will be detached, thus we decrease the counts by it.
    The new link is the link that will be attached, thus we increase the counts by it.
    """
    reference_link_child = egy.groupelementyear_set.filter(link_type=LinkTypes.REFERENCE.name).\
        values_list("child_branch", flat=True)
    parents = list(reference_link_child) + [egy.id]
    current_count = _get_education_group_types_count(parents)

    old_link_count = __get_link_children_count(old_link)
    new_link_count = __get_link_children_count(new_link)

    for type_name, count in old_link_count.items():
        if type_name in current_count:
            current_count[type_name] -= count

    for type_name, count in new_link_count.items():
        if type_name in current_count:
            current_count[type_name] += count
        else:
            current_count[type_name] = count

    return current_count


def __get_link_children_count(link):
    if not link:
        return {}
    elif link.link_type == LinkTypes.REFERENCE.name:
        return _get_education_group_types_count([link.child_branch])
    return {link.child_branch.education_group_type.name: 1}


def _get_education_group_types_count(parents):
    qs = GroupElementYear.objects.\
        filter(parent__in=parents). \
        exclude(child_branch=None). \
        filter(link_type=None).\
        annotate(education_group_type_name=F("child_branch__education_group_type__name")). \
        values("education_group_type_name"). \
        order_by("education_group_type_name").\
        annotate(count=Count("education_group_type_name"))

    return {record["education_group_type_name"]: record["count"] for record in qs}
