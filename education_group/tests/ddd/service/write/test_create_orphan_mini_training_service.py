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

from education_group.ddd.domain import mini_training
from education_group.ddd.service.write import create_orphan_mini_training_service
from education_group.tests.ddd.factories.command.create_mini_training_command import CreateMiniTrainingCommandFactory
from education_group.tests.ddd.factories.repository.group import get_fake_mini_training_repository
from testing.mocks import MockPatcherMixin


@mock.patch("education_group.ddd.domain.service.calculate_end_postponement."
            "CalculateEndPostponement.calculate_max_year_of_end_postponement", return_value=2022)
class TestCreateAndPostponeOrphanTraining(TestCase, MockPatcherMixin):
    def setUp(self) -> None:
        self.fake_mini_training_repository = get_fake_mini_training_repository([])
        self.mock_repo(
            "education_group.ddd.repository.mini_training.MiniTrainingRepository",
            self.fake_mini_training_repository
        )

    def test_should_return_mini_training_identities(self, mock_end_year_postponement):
        cmd = CreateMiniTrainingCommandFactory(year=2020, code="CODE", abbreviated_title="ACRON")

        result = create_orphan_mini_training_service.create_and_postpone_orphan_mini_training(cmd)

        expected_result = [mini_training.MiniTrainingIdentity(acronym="ACRON", year=year) for year in range(2020, 2023)]
        self.assertListEqual(expected_result, result)

    def test_should_postpone_values(self, mock_end_year_postponement):
        cmd = CreateMiniTrainingCommandFactory(year=2020, code="CODE", abbreviated_title="ACRON")

        identities = create_orphan_mini_training_service.create_and_postpone_orphan_mini_training(cmd)

        base_mini_training = self.fake_mini_training_repository.get(identities[0])
        for identity in identities[1:]:
            with self.subTest(year=identity.year):
                postponed_mini_training = self.fake_mini_training_repository.get(identity)
                self.assertTrue(postponed_mini_training.has_same_values_as(base_mini_training))
