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
from typing import List

from django.db.models import F

from attribution.ddd.domain.attribution import Attribution, Teacher
from attribution.models import attribution_charge_new


def __instanciate_teacher_object(attribution_data: dict) -> dict:
    attribution_data['teacher'] = Teacher(last_name=attribution_data.pop('teacher_last_name'),
                                          first_name=attribution_data.pop('teacher_first_name'),
                                          middle_name=attribution_data.pop('teacher_middle_name'),
                                          email=attribution_data.pop('teacher_email'),
                                          )

    return attribution_data


def load_attributions(acronym: str, year: int) -> List['Attribution']:

    qs = attribution_charge_new.AttributionChargeNew.objects \
        .filter(learning_component_year__learning_unit_year__acronym=acronym,
                learning_component_year__learning_unit_year__academic_year__year=year) \
        .select_related('learning_component_year', 'attribution__tutor__person')\
        .order_by('attribution__tutor__person__last_name',
                  'attribution__tutor__person__first_name',
                  'attribution__tutor__person__middle_name')\
        .annotate(teacher_last_name=F('attribution__tutor__person__last_name'),
                  teacher_first_name=F('attribution__tutor__person__first_name'),
                  teacher_middle_name=F('attribution__tutor__person__middle_name'),
                  teacher_email=F('attribution__tutor__person__email'),
                  )\
        .values('teacher_last_name', 'teacher_first_name',
                'teacher_middle_name', 'teacher_email')

    return [
        Attribution(**__instanciate_teacher_object(attribution_data))
        for attribution_data in qs
    ]
