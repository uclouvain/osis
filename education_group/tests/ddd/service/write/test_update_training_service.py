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
from education_group.tests.ddd.factories.training import TrainingFactory


class TestUpdateTraining(TestCase):
    @mock.patch("education_group.ddd.service.write.update_training_service.CalculateEndPostponement."
                "calculate_year_of_end_postponement", return_value=2020)
    @mock.patch("education_group.ddd.service.write.postpone_training_service.postpone_training")
    @mock.patch("education_group.ddd.repository.training.TrainingRepository", autospec=True)
    def test_should_update_and_save_training_when_training_exists(
            self,
            mock_repository,
            mock_postpone_training,
            mock_end_year_of_postponement):
        mock_repository.get.return_value = TrainingFactory()
        mock_postpone_training.return_value = None

        update_command = UpdateTrainingCommandFactory()
        result = update_training_service.update_training(update_command)

        expected_result = training.TrainingIdentity(acronym=update_command.abbreviated_title, year=update_command.year)
        self.assertEqual(expected_result, result)
        self.assertTrue(mock_repository.get.called)
        self.assertTrue(mock_repository.update.called)
        self.assertTrue(mock_postpone_training.called)
