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
from django.test import TestCase
from mock import patch

from education_group.ddd.domain import training
from education_group.ddd.service.write import update_training_service
from education_group.tests.ddd.factories.command.update_training_factory import UpdateTrainingCommandFactory
from education_group.tests.ddd.factories.repository.fake import get_fake_training_repository
from education_group.tests.ddd.factories.training import TrainingFactory
from testing.mocks import MockPatcherMixin


@patch("education_group.ddd.service.write.update_group_service.update_group")
@patch('education_group.ddd.service.write.update_training_service.postpone_training_service.'
       'postpone_training', return_value=[])
class TestUpdateTraining(TestCase, MockPatcherMixin):
    @classmethod
    def setUpTestData(cls):
        cls.cmd = UpdateTrainingCommandFactory(year=2018, abbreviated_title="MERC")

    def setUp(self) -> None:
        self.trainings = [TrainingFactory(entity_identity__year=year,
                                          entity_identity__acronym=self.cmd.abbreviated_title)
                          for year in range(2018, 2020)]
        self.fake_training_repo = get_fake_training_repository(self.trainings)
        self.mock_repo("education_group.ddd.repository.training.TrainingRepository", self.fake_training_repo)

    def test_should_return_identities(self, mock_postpone_training_service, mock_update_group):
        mock_postpone_training_service.return_value = [
            training.TrainingIdentity(acronym="MERC", year=year) for year in range(2019, 2021)
        ]

        result = update_training_service.update_training(self.cmd)

        expected_result = [training.TrainingIdentity(acronym="MERC", year=year) for year in range(2018, 2021)]
        self.assertListEqual(expected_result, result)

    def test_should_postpone_updates(self, mock_postpone_training_service, mock_update_group):
        update_training_service.update_training(self.cmd)

        self.assertTrue(mock_postpone_training_service.called)
