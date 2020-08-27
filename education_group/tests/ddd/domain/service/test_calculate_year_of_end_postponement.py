# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
import copy
from typing import List

import attr
import mock
from django.test import SimpleTestCase

from education_group.ddd.domain import training, group, exception
from education_group.ddd.domain.service import calculate_end_postponement
from education_group.tests.ddd.factories.group import GroupFactory
from education_group.tests.ddd.factories.repository.fake import get_fake_training_repository, get_fake_group_repository
from education_group.tests.ddd.factories.training import TrainingFactory
from testing.mocks import MockPatcherMixin


class TestCalculateMaxYearOfEndPostponement(SimpleTestCase, MockPatcherMixin):
    def setUp(self):
        self.starting_academic_year_year = 2020
        self.mock_starting_academic_year = self.mock_service(
            "base.models.academic_year.starting_academic_year",
            return_value=mock.Mock(year=self.starting_academic_year_year)
        )

    def test_should_return_starting_academic_year_plus_years_to_postpone(self):
        result = calculate_end_postponement.CalculateEndPostponement.calculate_max_year_of_end_postponement()
        self.assertEqual(
            2026,
            result
        )


class TestCalculateYearOfPostponementConflict(SimpleTestCase, MockPatcherMixin):
    def setUp(self) -> None:
        self.training_identity = training.TrainingIdentity(acronym="ACRO", year=2019)
        self.group_identity = group.GroupIdentity(code="CODE", year=2019)

        self.fake_training_repo = get_fake_training_repository([])
        self.mock_repo("education_group.ddd.repository.training.TrainingRepository", self.fake_training_repo)

        self.fake_group_repo = get_fake_group_repository([])
        self.mock_repo("education_group.ddd.repository.group.GroupRepository", self.fake_group_repo)

    def test_should_return_max_int_if_no_conflicts(self):
        self.fake_training_repo.root_entities = self._generate_trainings_with_no_conflicts()
        self.fake_group_repo.root_entities = self._generate_groups_with_no_conflicts()

        result = calculate_end_postponement.CalculateEndPostponement.calculate_year_of_postponement_conflict(
            self.training_identity,
            self.group_identity,
            self.fake_training_repo,
            self.fake_group_repo
        )

        self.assertEqual(calculate_end_postponement.MAX_YEAR - 1, result)

    def test_should_return_year_of_conflict_if_conflicts_present_for_trainings(self):
        self.fake_training_repo.root_entities = self._generate_trainings_with_conflicts()
        self.fake_group_repo.root_entities = self._generate_groups_with_no_conflicts()

        result = calculate_end_postponement.CalculateEndPostponement.calculate_year_of_postponement_conflict(
            self.training_identity,
            self.group_identity,
            self.fake_training_repo,
            self.fake_group_repo
        )

        self.assertEqual(2020 - 1, result)

    def test_should_return_year_of_conflict_if_conflicts_present_for_groups(self):
        self.fake_training_repo.root_entities = self._generate_trainings_with_no_conflicts()
        self.fake_group_repo.root_entities = self._generate_groups_with_conflicts()

        result = calculate_end_postponement.CalculateEndPostponement.calculate_year_of_postponement_conflict(
            self.training_identity,
            self.group_identity,
            self.fake_training_repo,
            self.fake_group_repo
        )

        self.assertEqual(2020 - 1, result)

    def _generate_trainings_with_no_conflicts(self) -> List['training.Training']:
        initial_training = TrainingFactory(entity_identity=self.training_identity)
        next_training = copy.copy(initial_training)
        next_training.entity_id = attr.evolve(initial_training.entity_id, year=initial_training.entity_id.year+1)
        next_training.entity_identity = next_training.entity_id

        return [initial_training, next_training]

    def _generate_trainings_with_conflicts(self) -> List['training.Training']:
        initial_training = TrainingFactory(entity_identity=self.training_identity)
        next_training = TrainingFactory()
        next_training.entity_id = attr.evolve(initial_training.entity_id, year=initial_training.entity_id.year+1)
        next_training.entity_identity = next_training.entity_id

        return [initial_training, next_training]

    def _generate_groups_with_no_conflicts(self) -> List['group.Group']:
        initial_group = GroupFactory(entity_identity=self.group_identity)
        next_group = copy.copy(initial_group)
        next_group.entity_id = attr.evolve(initial_group.entity_id, year=initial_group.entity_id.year+1)
        next_group.entity_identity = next_group.entity_id

        return [initial_group, next_group]

    def _generate_groups_with_conflicts(self) -> List['group.Group']:
        initial_group = GroupFactory(entity_identity=self.group_identity)
        next_group = GroupFactory()
        next_group.entity_id = attr.evolve(initial_group.entity_id, year=initial_group.entity_id.year+1)
        next_group.entity_identity = next_group.entity_id

        return [initial_group, next_group]
