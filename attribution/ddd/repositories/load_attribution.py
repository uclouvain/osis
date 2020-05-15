##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from typing import List, Dict

from django.db.models import F

from attribution.ddd.domain.attribution import Teacher, Attribution
from attribution.ddd.domain.teacher import Teacher
from attribution.models import attribution_charge_new
from django.db.models import QuerySet


def __instanciate_teacher_object(attribution_data: dict) -> dict:
    return Teacher(last_name=attribution_data.pop('teacher_last_name'),
                   first_name=attribution_data.pop('teacher_first_name'),
                   middle_name=attribution_data.pop('teacher_middle_name'),
                   email=attribution_data.pop('teacher_email'),
                   )


def load_attributions(learning_unit_year_ids: List[int]) -> QuerySet:
    return attribution_charge_new.AttributionChargeNew.objects \
        .filter(learning_component_year__learning_unit_year__id__in=learning_unit_year_ids) \
        .select_related('learning_component_year', 'attribution__tutor__person') \
        .order_by('attribution__tutor__person__last_name',
                  'attribution__tutor__person__first_name',
                  'attribution__tutor__person__middle_name') \
        .annotate(teacher_last_name=F('attribution__tutor__person__last_name'),
                  teacher_first_name=F('attribution__tutor__person__first_name'),
                  teacher_middle_name=F('attribution__tutor__person__middle_name'),
                  teacher_email=F('attribution__tutor__person__email'),
                  ue_id=F('learning_component_year__learning_unit_year__id')
                  ) \
        .values('teacher_last_name', 'teacher_first_name',
                'teacher_middle_name', 'teacher_email', 'ue_id')


def set_attributions(attributions_dict: Dict = None) -> List['Attribution']:
    attributions = []
    for teacher_data in attributions_dict:
        attributions.append(
            Attribution(
                teacher=__instanciate_teacher_object(teacher_data)
                )
            )
    return attributions
