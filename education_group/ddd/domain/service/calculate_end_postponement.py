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
import sys
from typing import Type

import attr

from base.models import academic_year
from education_group.ddd.business_types import *
from education_group.ddd.domain import exception
from osis_common.ddd import interface

DEFAULT_YEARS_TO_POSTPONE = 6
MAX_YEAR = sys.maxsize


class CalculateEndPostponement(interface.DomainService):
    @classmethod
    def calculate_year_of_postponement(
            cls,
            training_identity: 'TrainingIdentity',
            group_identity: 'GroupIdentity',
            training_repository: Type['TrainingRepository'],
            group_repository: Type['GroupRepository']) -> int:
        return min(
            cls.calculate_max_year_of_end_postponement(),
            cls.calculate_year_of_postponement_conflict(
                training_identity,
                group_identity,
                training_repository,
                group_repository
            )
        )

    @classmethod
    def calculate_year_of_postponement_for_mini_training(
            cls,
            mini_training_identity: 'MiniTrainingIdentity',
            group_identity: 'GroupIdentity',
            mini_training_repository: Type['MiniTrainingRepository'],
            group_repository: Type['GroupRepository']) -> int:
        return min(
            cls.calculate_max_year_of_end_postponement(),
            cls.calculate_year_of_postponement_conflict_for_mini_training(
                mini_training_identity,
                group_identity,
                mini_training_repository,
                group_repository
            )
        )

    @classmethod
    def calculate_max_year_of_end_postponement(cls) -> int:
        return academic_year.starting_academic_year().year + DEFAULT_YEARS_TO_POSTPONE

    @classmethod
    def calculate_year_of_postponement_conflict(
            cls,
            training_identity: 'TrainingIdentity',
            group_identity: 'GroupIdentity',
            training_repository: Type['TrainingRepository'],
            group_repository: Type['GroupRepository']) -> int:
        year_training_conflict = MAX_YEAR
        current_training = training_repository.get(training_identity)
        for year in itertools.count(training_identity.year + 1):
            nex_year_identity = attr.evolve(training_identity, year=year)
            try:
                next_training = training_repository.get(nex_year_identity)
            except exception.TrainingNotFoundException:
                break
            if not current_training.has_same_values_as(next_training):
                year_training_conflict = year
                break
            current_training = next_training

        year_group_conflict = MAX_YEAR
        current_group = group_repository.get(group_identity)
        for year in itertools.count(group_identity.year + 1):
            nex_year_identity = attr.evolve(group_identity, year=year)
            try:
                next_group = group_repository.get(nex_year_identity)
            except exception.GroupNotFoundException:
                break
            if not current_group.has_same_values_as(next_group):
                year_group_conflict = year
                break
            current_group = next_group

        return min(year_training_conflict, year_group_conflict) - 1

    @classmethod
    def calculate_year_of_postponement_conflict_for_mini_training(
            cls,
            mini_training_identity: 'MiniTrainingIdentity',
            group_identity: 'GroupIdentity',
            mini_training_repository: Type['MiniTrainingRepository'],
            group_repository: Type['GroupRepository']) -> int:
        year_mini_training_conflict = MAX_YEAR
        current_training = mini_training_repository.get(mini_training_identity)
        for year in itertools.count(mini_training_identity.year + 1):
            nex_year_identity = attr.evolve(mini_training_identity, year=year)
            try:
                next_mini_training = mini_training_repository.get(nex_year_identity)
            except exception.MiniTrainingNotFoundException:
                break
            if not current_training.has_same_values_as(next_mini_training):
                year_mini_training_conflict = year
                break
            current_training = next_mini_training

        year_group_conflict = MAX_YEAR
        current_group = group_repository.get(group_identity)
        for year in itertools.count(group_identity.year + 1):
            nex_year_identity = attr.evolve(group_identity, year=year)
            try:
                next_group = group_repository.get(nex_year_identity)
            except exception.GroupNotFoundException:
                break
            if not current_group.has_same_values_as(next_group):
                year_group_conflict = year
                break
            current_group = next_group

        return min(year_mini_training_conflict, year_group_conflict) - 1
