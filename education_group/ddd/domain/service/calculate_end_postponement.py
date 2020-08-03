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
from typing import Type

import attr

from base.models import academic_year
from education_group.ddd.business_types import *
from osis_common.ddd import interface

DEFAULT_YEARS_TO_POSTPONE = 6


class CalculateEndPostponement(interface.DomainService):

    @classmethod
    def calculate_year_of_end_postponement(
            cls,
            training: 'Training',
            training_repository: Type['TrainingRepository'],
            group: 'Group',
            group_repository: Type['GroupRepository']
    ) -> int:
        max_year_to_postpone = cls._compute_max_year_to_postpone(training)

        max_year_to_postpone_for_training = cls._compute_postponement_end_year_training(
            training,
            max_year_to_postpone,
            training_repository
        )
        max_year_to_postpone_for_group = cls._compute_postponement_end_year_group(
            group,
            max_year_to_postpone,
            group_repository
        )
        return min(max_year_to_postpone_for_group, max_year_to_postpone_for_training)

    @classmethod
    def _compute_max_year_to_postpone(cls, training: 'Training') -> int:
        current_year = academic_year.starting_academic_year().year
        max_year_to_postpone = current_year + DEFAULT_YEARS_TO_POSTPONE

        is_end_year_inferior_to_max_year_to_postpone = training.end_year and training.end_year < max_year_to_postpone
        if is_end_year_inferior_to_max_year_to_postpone:
            return training.end_year

        return max_year_to_postpone

    @classmethod
    def _compute_postponement_end_year_training(
            cls,
            training: 'Training',
            max_year_to_postpone,
            repository: Type['TrainingRepository']) -> int:
        training_identities = [
            attr.evolve(training.entity_identity, year=year)
            for year in range(training.year+1, max_year_to_postpone+1)
        ]
        next_year_trainings = repository.search(entity_ids=training_identities)
        next_year_trainings_ordered_by_year = sorted(next_year_trainings, key=lambda obj: obj.year)

        current_training = training
        for training_obj in next_year_trainings_ordered_by_year:
            if not current_training.has_same_values_as(training_obj):
                return current_training.year
            current_training = training_obj
        return max_year_to_postpone

    @classmethod
    def _compute_postponement_end_year_group(
            cls,
            group: 'Group',
            max_year_to_postpone,
            repository: Type['GroupRepository']) -> int:
        group_identities = [
            attr.evolve(group.entity_identity, year=year)
            for year in range(group.year + 1, max_year_to_postpone + 1)
        ]
        next_year_groups = repository.search(entity_ids=group_identities)
        next_year_groups_ordered_by_year = sorted(next_year_groups, key=lambda obj: obj.year)

        current_group = group
        for group_obj in next_year_groups_ordered_by_year:
            if not current_group.has_same_values_as(group_obj):
                return current_group.year
            current_group = group_obj
        return max_year_to_postpone
