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
import attr
from django.test import TestCase

from education_group.ddd import command
from education_group.ddd.domain import exception, training, group
from education_group.ddd.service.read import get_update_training_warning_messages
from education_group.tests.ddd.factories.group import GroupFactory
from education_group.tests.ddd.factories.repository.fake import get_fake_training_repository, get_fake_group_repository
from education_group.tests.ddd.factories.training import TrainingFactory
from testing.mocks import MockPatcherMixin


class TestGetWarningMessages(TestCase, MockPatcherMixin):
    def setUp(self):
        self.fake_training_repo = get_fake_training_repository([])
        self.mock_repo("education_group.ddd.repository.training.TrainingRepository", self.fake_training_repo)

        self.fake_group_repo = get_fake_group_repository([])
        self.mock_repo("education_group.ddd.repository.group.GroupRepository", self.fake_group_repo)

        self.initial_training = TrainingFactory(entity_identity__year=2020)
        self.initial_group = GroupFactory(entity_identity__year=2020)

        self.cmd = command.GetUpdateTrainingWarningMessages(
            acronym=self.initial_training.acronym,
            code=self.initial_group.code,
            year=self.initial_training.year
        )

    def test_should_return_empty_list_when_no_difference_through_the_years(self):
        self.fake_training_repo.root_entities = [
            self.initial_training,
            self._generate_next_year_training_with_same_values(self.initial_training)
        ]
        self.fake_group_repo.root_entities = [
            self.initial_group,
            self._generate_next_year_group_with_same_value(self.initial_group)
        ]

        result = get_update_training_warning_messages.get_conflicted_fields(self.cmd)
        self.assertFalse(result)

    def test_should_return_not_empty_list_when_difference_through_the_years(self):
        self.fake_training_repo.root_entities = [
            self.initial_training,
            self._generate_next_year_training_with_different_values(self.initial_training)
        ]
        self.fake_group_repo.root_entities = [
            self.initial_group,
            self._generate_next_year_group_with_different_values(self.initial_group)
        ]

        result = get_update_training_warning_messages.get_conflicted_fields(self.cmd)
        self.assertTrue(result)

    def _generate_next_year_training_with_same_values(
            self,
            source_training: 'training.Training') -> 'training.Training':
        next_year_identity = attr.evolve(source_training.entity_id, year=source_training.entity_id.year+1)
        return attr.evolve(source_training, entity_identity=next_year_identity, entity_id=next_year_identity)

    def _generate_next_year_group_with_same_value(
            self,
            source_group: 'group.Group') -> 'group.Group':
        next_year_identity = attr.evolve(source_group.entity_id, year=source_group.entity_id.year+1)
        return attr.evolve(source_group, entity_identity=next_year_identity, entity_id=next_year_identity)

    def _generate_next_year_training_with_different_values(
            self,
            source_training: 'training.Training') -> 'training.Training':
        next_year_identity = attr.evolve(source_training.entity_id, year=source_training.entity_id.year+1)
        return TrainingFactory(entity_identity=next_year_identity)

    def _generate_next_year_group_with_different_values(
            self,
            source_group: 'group.Group') -> 'group.Group':
        next_year_identity = attr.evolve(source_group.entity_id, year=source_group.entity_id.year + 1)
        return GroupFactory(entity_identity=next_year_identity)
