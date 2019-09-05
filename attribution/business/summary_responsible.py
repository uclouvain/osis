##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.core.exceptions import PermissionDenied

from attribution import models as mdl_attr
from attribution.models.attribution import search_by_learning_unit_this_year
from base import models as mdl_base
from base.models.entity_manager import find_entities_with_descendants_from_entity_managers


def get_learning_unit_year_managed_by_user_from_id(user, learning_unit_year_id):
    a_learning_unit_year = mdl_base.learning_unit_year.get_by_id(learning_unit_year_id)
    if _is_user_manager_of_entity_allocation_of_learning_unit_year(user, a_learning_unit_year):
        return a_learning_unit_year
    raise PermissionDenied("User is not an entity manager of the allocation entity of the learning unit.")


def _is_user_manager_of_entity_allocation_of_learning_unit_year(user, a_learning_unit_year):
    entities_manager = mdl_base.entity_manager.find_by_user(user)
    entities_with_descendants = find_entities_with_descendants_from_entity_managers(entities_manager)
    return a_learning_unit_year.allocation_entity in entities_with_descendants


def search_attributions(academic_year, entities_manager=None, course_code=None, learning_unit_title=None,
                        tutor=None, summary_responsible=None):
    if entities_manager is None:
        entities_manager = []
    entities_with_descendants = find_entities_with_descendants_from_entity_managers(entities_manager)
    learning_unit_year_attributions_queryset = search_by_learning_unit_this_year(
        course_code,
        learning_unit_title,
        academic_year=academic_year,
    )
    attributions = mdl_attr.attribution.filter_attributions(
        attributions_queryset=learning_unit_year_attributions_queryset,
        entities=entities_with_descendants,
        tutor=tutor,
        responsible=summary_responsible,
    )
    return list(attributions)


def get_attributions_data(user, learning_unit_year_id, responsibles_order):
    a_learning_unit_year = get_learning_unit_year_managed_by_user_from_id(user, learning_unit_year_id)
    return {
        'learning_unit_year': a_learning_unit_year,
        'attributions': mdl_attr.attribution.find_all_responsible_by_learning_unit_year(
            a_learning_unit_year, responsibles_order=responsibles_order),
        'academic_year': a_learning_unit_year.academic_year
    }
