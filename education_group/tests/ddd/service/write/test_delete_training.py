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
from unittest import mock

from django.test import TestCase

from education_group.ddd import command
from education_group.ddd.domain import exception, training
from education_group.ddd.service.write import delete_training_service


class TestDeleteTraining(TestCase):
    @mock.patch("education_group.ddd.repository.training.TrainingRepository", autospec=True)
    def test_delete_trainings(self, mock_training_repository):
        mock_training_repository.delete.side_effect = [None, None, exception.TrainingNotFoundException]

        delete_command = command.DeleteTrainingCommand(acronym="Acronym", from_year=2018)
        result = delete_training_service.delete_training(delete_command)

        self.assertListEqual(
            [
                training.TrainingIdentity(acronym="Acronym", year=2018),
                training.TrainingIdentity(acronym="Acronym", year=2019)
            ],
            result
        )
        self.assertEqual(3, mock_training_repository.delete.call_count)
