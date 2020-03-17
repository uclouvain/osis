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

import copy
from typing import List, Dict, Any

from django.db.models import Case, F, When, IntegerField

from base.models.enums.link_type import LinkTypes
from base.models.group_element_year import GroupElementYear
from base.models.learning_unit_year import LearningUnitYear as LearningUnitYearModel
from learning_unit.ddd.domain.learning_unit_year import LearningUnitYear


def load_multiple(learning_unit_year_ids: List[int]) -> List['LearningUnitYear']:
    qs = LearningUnitYearModel.objects.filter(pk__in=learning_unit_year_ids).annotate(
        specific_title_en=F('specific_title_english'),
        specific_title_fr=F('specific_title'),
        common_title_fr=F('learning_container_year__common_title'),
        common_title_en=F('learning_container_year__common_title_english'),
        year=F('academic_year__year'),
        proposal_type=F('proposallearningunit__type'),
        start_year=F('learning_unit__start_year'),
        end_year=F('learning_unit__end_year'),
    ).values(
        'id',
        'year',
        'acronym',
        'specific_title_fr',
        'specific_title_en',
        'common_title_fr',
        'common_title_en',
        'start_year',
        'end_year',
        'proposal_type',
        'credits',
        'status',
        'periodicity'
    )
    return [LearningUnitYear(**learnin_unit_data) for learnin_unit_data in qs]
