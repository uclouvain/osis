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
from base.models.enums.link_type import LinkTypes
from base.models.exceptions import IncompatiblesTypesException
from base.models.group_element_year import GroupElementYear
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
    def _is_max_child_reached(number_children, authorized_relationship):
        max_count = authorized_relationship.max_count_authorized
        return max_count and number_children >= max_count

    return _is_limit_child_reached(parent, child_education_group_type, _is_max_child_reached)


def is_min_child_reached(parent, child_education_group_type):
    def _is_min_child_reached(number_children, authorized_relationship):
        min_count = authorized_relationship.min_count_authorized
        return bool(min_count) and number_children <= authorized_relationship.min_count_authorized

    return _is_limit_child_reached(parent, child_education_group_type, _is_min_child_reached)


def _is_limit_child_reached(parent, child_education_group_type, boolean_func):
    """ Fetch the number of children with the same type """
    number_children_of_same_type = parent.groupelementyear_set.filter(
        child_branch__education_group_type=child_education_group_type
    ).count()

    # Add children of reference links.
    for link in parent.groupelementyear_set.all():
        if link.link_type == LinkTypes.REFERENCE.name and link.child_branch:
            number_children_of_same_type += link.child_branch.groupelementyear_set.filter(
                child_branch__education_group_type=child_education_group_type
            ).count()

    try:
        auth_rel = parent.education_group_type.authorized_parent_type.get(
            child_type=child_education_group_type,
        )
    except AuthorizedRelationship.DoesNotExist:
        return True
    return boolean_func(number_children_of_same_type, auth_rel)


def compute_number_children(egy, child, link_type):
    reference_link_child = egy.groupelementyear_set.exclude(child_branch=child).\
        filter(link_type=LinkTypes.REFERENCE.name).\
        values_list("child_branch", flat=True)

    education_group_types_count = GroupElementYear.objects.\
        filter(Q(parent__in=reference_link_child) | Q(parent=egy)).exclude(Q(parent=egy) & Q(child_branch=child)).\
        filter(link_type=None).\
        exclude(child_branch=None). \
        annotate(education_group_type=F("child_branch__education_group_type")). \
        values("education_group_type"). \
        order_by("education_group_type").\
        annotate(count=Count("education_group_type"))

    number_children = defaultdict(int)
    for record in education_group_types_count:
        number_children[record["education_group_type"]] += record["count"]

    if link_type == LinkTypes.REFERENCE.name:
        count = GroupElementYear.objects.filter(parent=child). \
            exclude(child_branch=None). \
            annotate(education_group_type=F("child_branch__education_group_type")). \
            values("education_group_type"). \
            order_by("education_group_type").\
            annotate(count=Count("education_group_type"))
        for c in count:
            number_children[c["education_group_type"]] += c["count"]
    else:
        number_children[child.education_group_type.id] += 1

    return number_children
