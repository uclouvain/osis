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
from education_group.ddd.service.write import create_orphan_training_service
from education_group.tests.ddd.factories.command.create_training_command import CreateTrainingCommandFactory
from education_group.tests.ddd.factories.repository.fake import get_fake_training_repository
from testing.mocks import MockPatcherMixin


@mock.patch("education_group.ddd.domain.service.calculate_end_postponement."
            "CalculateEndPostponement.calculate_max_year_of_end_postponement", return_value=2021)
class TestCreateAndPostponeOrphanTraining(TestCase, MockPatcherMixin):
    def setUp(self) -> None:
        self.fake_training_repository = get_fake_training_repository([])
        self.mock_repo("education_group.ddd.repository.training.TrainingRepository", self.fake_training_repository)

    def test_should_return_identities(self, mock_end_year_postponement):
        cmd = CreateTrainingCommandFactory(year=2018)

        result = create_orphan_training_service.create_and_postpone_orphan_training(cmd)
        expected_result = [training.TrainingIdentity(acronym=cmd.abbreviated_title, year=year)
                           for year in range(2018, 2022)]
        self.assertListEqual(expected_result, result)

    def test_should_postpone_creation(self, mock_end_year_postponement):
        cmd = CreateTrainingCommandFactory(year=2018)

        identities = create_orphan_training_service.create_and_postpone_orphan_training(cmd)

        base_training = self.fake_training_repository.get(identities[0])

        for identity in identities[1:]:
            with self.subTest(year=identity.year):
                postponed_training = self.fake_training_repository.get(identity)
                self.assertTrue(postponed_training.has_same_values_as(base_training))
