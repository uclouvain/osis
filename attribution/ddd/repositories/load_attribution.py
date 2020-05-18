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
import itertools
from typing import List, Dict

from django.db.models import F, Q

from attribution.ddd.domain.attribution import Attribution
from attribution.ddd.domain.teacher import Teacher
from attribution.models import attribution_charge_new
from learning_unit.ddd.domain.learning_unit_year import LearningUnitYearIdentity


def load_attributions(learning_unit_year_ids: List['LearningUnitYearIdentity']) \
        -> Dict[LearningUnitYearIdentity, List['Attribution']]:
    qs = attribution_charge_new.AttributionChargeNew.objects.all()
    filter_search_from = __build_where_clause(learning_unit_year_ids[0])
    for identity in learning_unit_year_ids[1:]:
        filter_search_from |= __build_where_clause(identity)
    qs = qs.filter(filter_search_from)
    qs = qs\
        .select_related('learning_component_year', 'attribution__tutor__person') \
        .order_by('attribution__tutor__person__last_name',
                  'attribution__tutor__person__first_name',
                  'attribution__tutor__person__middle_name') \
        .annotate(teacher_last_name=F('attribution__tutor__person__last_name'),
                  teacher_first_name=F('attribution__tutor__person__first_name'),
                  teacher_middle_name=F('attribution__tutor__person__middle_name'),
                  teacher_email=F('attribution__tutor__person__email'),
                  acronym_ue=F('learning_component_year__learning_unit_year__acronym'),
                  year_ue=F('learning_component_year__learning_unit_year__academic_year__year'),
                  ) \
        .values('teacher_last_name', 'teacher_first_name',
                'teacher_middle_name', 'teacher_email', 'acronym_ue', 'year_ue')

    return _build_sorted_attributions_grouped_by_ue(qs)


def __build_where_clause(learning_unit_identity: 'LearningUnitYearIdentity') -> Q:
    return Q(
            learning_component_year__learning_unit_year__acronym=learning_unit_identity.code,
            learning_component_year__learning_unit_year__academic_year__year=learning_unit_identity.year
        )


def _build_sorted_attributions_grouped_by_ue(qs_attributions) -> Dict[LearningUnitYearIdentity, List['Attribution']]:
    sorted_attributions = sorted(qs_attributions,
                                 key=lambda attribution: (attribution['acronym_ue'],
                                                          attribution['year_ue'],
                                                          attribution['teacher_last_name'],
                                                          attribution['teacher_first_name'],
                                                          attribution['teacher_middle_name']
                                                          )
                                 )
    sorted_attributions_grouped_by_ue = {}

    for learning_unit_year_id, attributions in itertools.groupby(sorted_attributions,
                                                                 key=lambda attribution: (attribution['acronym_ue'],
                                                                                          attribution['year_ue'])
                                                                 ):
        learning_unit_identity = LearningUnitYearIdentity(code=learning_unit_year_id[0], year=learning_unit_year_id[1])
        attributions_data = []
        for attribution in attributions:
            attributions_data.append(instanciate_attribution(attribution))
        sorted_attributions_grouped_by_ue.update({learning_unit_identity: attributions_data})
    return sorted_attributions_grouped_by_ue


def instanciate_attribution(attributions_dict: Dict = None) -> 'Attribution':
    return Attribution(teacher=instanciate_teacher_object(attributions_dict))


def instanciate_teacher_object(attribution_data: dict) -> Teacher:
    return Teacher(last_name=attribution_data.get('teacher_last_name'),
                   first_name=attribution_data.get('teacher_first_name'),
                   middle_name=attribution_data.get('teacher_middle_name'),
                   email=attribution_data.get('teacher_email'),
                   )
