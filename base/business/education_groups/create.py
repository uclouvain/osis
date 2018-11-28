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

from base.models.education_group import EducationGroup
from base.models.education_group_year import EducationGroupYear

REGEX_TRAINING_PARTIAL_ACRONYM = r"^(?P<sigle_ele>[A-Z]{3,5})\d{3}[A-Z]$"
REGEX_GROUP_PARTIAL_ACRONYM_INITIAL_VALUE = r"^(?P<cnum>\d{3})(?P<subdivision>[A-Z])$"


def create_child(parent_egy, child_education_group_type, validation_rule_title, validation_rule_partial_acronym):
    child_egy = EducationGroupYear(
        academic_year=parent_egy.academic_year,
        main_teaching_campus=parent_egy.main_teaching_campus,
        management_entity=parent_egy.management_entity,
        education_group_type=child_education_group_type,
        title=validation_rule_title.initial_value,
        partial_acronym=_compose_child_partial_acronym(parent_egy.partial_acronym,
                                                       validation_rule_partial_acronym.initial_value),
        acronym=_compose_child_acronym(parent_egy.acronym, validation_rule_title.initial_value),
        education_group=_create_child_education_group(parent_egy.academic_year.year)
    )
    child_egy.save()
    return child_egy


def _create_child_education_group(year):
    eg = EducationGroup(
        start_year=year,
        end_year=year
    )
    eg.save()
    return eg


def _compose_child_acronym(parent_acronym, child_title_initial_value):
    return "{child_title}{parent_acronym}".format(
        child_title=child_title_initial_value.replace(" ", "").upper(),
        parent_acronym=parent_acronym
    )


def _compose_child_partial_acronym(parent_partial_acronym, child_initial_value):
    reg_parent_partial_acronym = re.compile(REGEX_TRAINING_PARTIAL_ACRONYM)
    match_result = reg_parent_partial_acronym.search(parent_partial_acronym)
    sigle_ele = match_result.group("sigle_ele")

    reg_child_initial_value = re.compile(REGEX_GROUP_PARTIAL_ACRONYM_INITIAL_VALUE)
    match_result = reg_child_initial_value.search(child_initial_value)
    cnum, subdivision = match_result.group("cnum", "subdivision")

    partial_acronym = "{}{}{}".format(sigle_ele, cnum, subdivision)
    while EducationGroupYear.objects.filter(partial_acronym=partial_acronym).exists():
        # FIXME Should take into account overflow > 999
        cnum = str(int(cnum) + 1)
        partial_acronym = "{}{}{}".format(sigle_ele, cnum, subdivision)

    return partial_acronym

