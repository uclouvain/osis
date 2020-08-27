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
import mock
from django.test import TestCase

from education_group.ddd.domain import training
from education_group.ddd.service.write import update_training_service
from education_group.tests.ddd.factories.command.update_training_factory import UpdateTrainingCommandFactory
from education_group.tests.ddd.factories.repository.fake import get_fake_training_repository
from education_group.tests.ddd.factories.training import TrainingFactory
from testing.mocks import MockPatcherMixin


@mock.patch("education_group.ddd.domain.service.calculate_end_postponement."
            "CalculateEndPostponement.calculate_year_of_postponement", return_value=2020)
class TestUpdateTraining(TestCase, MockPatcherMixin):
    def setUp(self) -> None:
        self.trainings = [TrainingFactory(entity_identity__year=year, entity_identity__acronym="MERC")
                          for year in range(2018, 2020)]
        self.fake_training_repo = get_fake_training_repository(self.trainings)
        self.mock_repo("education_group.ddd.repository.training.TrainingRepository", self.fake_training_repo)

    def test_should_return_identities(self, mock_end_year_of_postponement):
        update_command = UpdateTrainingCommandFactory(year=2018, abbreviated_title="MERC")

        result = update_training_service.update_training(update_command)

        expected_result = [training.TrainingIdentity(acronym="MERC", year=year) for year in range(2018, 2021)]
        self.assertListEqual(expected_result, result)

    def test_should_postpone_updates(self, mock_end_year_of_postponement):
        update_command = UpdateTrainingCommandFactory(year=2018, abbreviated_title="MERC")

        identities = update_training_service.update_training(update_command)

        base_training = self.fake_training_repo.get(identities[0])

        for identity in identities[1:]:
            with self.subTest(year=identity.year):
                postponed_training = self.fake_training_repo.get(identity)
                self.assertTrue(postponed_training.has_same_values_as(base_training))

