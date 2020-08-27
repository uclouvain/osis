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
from typing import Union

from base.models import academic_year
from education_group.ddd.business_types import *
from education_group.ddd.domain.training import TrainingIdentity
from osis_common.ddd import interface
from program_management.ddd.domain.program_tree import ProgramTreeIdentity
from program_management.ddd.domain.service.identity_search import TrainingOrMiniTrainingOrGroupIdentitySearch


DEFAULT_YEARS_TO_POSTPONE = 6


class CalculateEndPostponement(interface.DomainService):

    @classmethod
    def calculate_end_postponement_year(
            cls,
            identity: Union['TrainingIdentity', 'MiniTrainingIdentity'],
            repository: Union['TrainingRepository', 'MiniTrainingRepository']
    ) -> int:
        max_year = _calculate_max_year_of_end_postponement()
        training = repository.get(identity)
        if training.end_year is None:
            return max_year
        return min(max_year, training.end_year)

    @classmethod
    def calculate_program_tree_end_postponement(
            cls,
            identity: 'ProgramTreeIdentity',
            training_repository: 'TrainingRepository',
            mini_training_repository: 'MiniTrainingRepository'
    ) -> int:
        root_identity = TrainingOrMiniTrainingOrGroupIdentitySearch.get_from_program_tree_identity(identity)
        return cls.calculate_end_postponement_year(
            identity=root_identity,
            repository=training_repository if isinstance(root_identity, TrainingIdentity) else mini_training_repository,
        )


def _calculate_max_year_of_end_postponement() -> int:
    default_years_to_postpone = DEFAULT_YEARS_TO_POSTPONE
    current_year = academic_year.starting_academic_year().year
    return default_years_to_postpone + current_year
