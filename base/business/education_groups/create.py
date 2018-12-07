##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
import re
from collections import defaultdict

from base.models.authorized_relationship import AuthorizedRelationship
from base.models.education_group import EducationGroup
from base.models.education_group_year import EducationGroupYear
from base.models.enums import count_constraint
from base.models.group_element_year import GroupElementYear
from base.models.validation_rule import ValidationRule

REGEX_TRAINING_PARTIAL_ACRONYM = r"^(?P<sigle_ele>[A-Z]{3,5})\d{3}[A-Z]$"
REGEX_GROUP_PARTIAL_ACRONYM_INITIAL_VALUE = r"^(?P<cnum>\d{3})(?P<subdivision>[A-Z])$"
MAX_CNUM = 999
WIDTH_CNUM = 3


def create_children(parent_egys):
    children_dict = defaultdict(list)
    if not parent_egys:
        return children_dict

    auth_rels = AuthorizedRelationship.objects.filter(
        parent_type=parent_egys[0].education_group_type,
        min_count_authorized=count_constraint.ONE
    )
    for relationship in auth_rels:
        child_education_group_type = relationship.child_type

        egy_title_reference = field_reference("title", EducationGroupYear, child_education_group_type)
        egy_partial_acronym_reference = field_reference("partial_acronym", EducationGroupYear,
                                                        child_education_group_type)
        validation_rule_partial_acronym = ValidationRule.objects.get(pk=egy_partial_acronym_reference)
        validation_rule_title = ValidationRule.objects.get(pk=egy_title_reference)
        partial_acronym = _compose_child_partial_acronym(parent_egys[0].partial_acronym,
                                                         validation_rule_partial_acronym.initial_value,
                                                         parent_egys[0], child_education_group_type)
        for parent_egy in parent_egys:
            title = _compose_child_title(validation_rule_title.initial_value, parent_egy.acronym)
            acronym = _compose_child_acronym(parent_egy.acronym, validation_rule_title.initial_value)
            grp_ele = create_child(parent_egy, child_education_group_type, title, partial_acronym, acronym)
            children_dict[parent_egy.id].append(grp_ele)
    return children_dict


def create_child(parent_egy, child_education_group_type, title, partial_acronym, acronym):
    try:
        existing_children = GroupElementYear.objects.get(
            parent=parent_egy,
            child_branch__education_group_type=child_education_group_type,
        )
    except GroupElementYear.DoesNotExist:
        pass
    else:
        return existing_children

    child_egy = EducationGroupYear(
        academic_year=parent_egy.academic_year,
        main_teaching_campus=parent_egy.main_teaching_campus,
        management_entity=parent_egy.management_entity,
        education_group_type=child_education_group_type,
        title=title,
        partial_acronym=partial_acronym,
        acronym=acronym,
        education_group=_create_child_education_group(parent_egy.academic_year.year)
    )
    child_egy.save()
    grp_ele = _append_child_to_parent(parent_egy, child_egy)
    return grp_ele


# FIXME Generalize method
def field_reference(name, model, education_group_type):
    return '.'.join([model._meta.db_table, name]) + '.' + education_group_type.external_id


def _create_child_education_group(year):
    eg = EducationGroup(start_year=year, end_year=year)
    eg.save()
    return eg


def _append_child_to_parent(parent_egy, child_egy):
    grp_ele = GroupElementYear(
        parent=parent_egy,
        child_branch=child_egy
    )
    grp_ele.save()
    return grp_ele


def _compose_child_title(child_title_initial_value, parent_acronym):
    return "{child_title} {parent_acronym}".format(
        child_title=child_title_initial_value,
        parent_acronym=parent_acronym
    )


def _compose_child_acronym(parent_acronym, child_title_initial_value):
    return "{child_title}{parent_acronym}".format(
        child_title=child_title_initial_value.replace(" ", "").upper(),
        parent_acronym=parent_acronym
    )


def _compose_child_partial_acronym(parent_partial_acronym, child_initial_value, parent, child_type):
    try:
        previous_children = GroupElementYear.objects.get(
            parent__education_group=parent.education_group,
            parent__academic_year__year=parent.academic_year.year - 1,
            child_branch__education_group_type=child_type
        )
    except GroupElementYear.DoesNotExist:
        pass
    else:
        return previous_children.child_branch.partial_acronym

    reg_parent_partial_acronym = re.compile(REGEX_TRAINING_PARTIAL_ACRONYM)
    match_result = reg_parent_partial_acronym.search(parent_partial_acronym)
    sigle_ele = match_result.group("sigle_ele")

    reg_child_initial_value = re.compile(REGEX_GROUP_PARTIAL_ACRONYM_INITIAL_VALUE)
    match_result = reg_child_initial_value.search(child_initial_value)
    cnum, subdivision = match_result.group("cnum", "subdivision")

    partial_acronym = "{}{}{}".format(sigle_ele, cnum, subdivision)
    # FIXME can be done in one query
    while EducationGroupYear.objects.filter(partial_acronym=partial_acronym).exists():
        # FIXME Can cnum surpass 1000
        cnum = "{:0{width}d}".format(
            (int(cnum) + 1) % MAX_CNUM,
            width=WIDTH_CNUM
        )
        partial_acronym = "{}{}{}".format(sigle_ele, cnum, subdivision)

    return partial_acronym
