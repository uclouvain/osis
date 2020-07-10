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
from education_group.ddd.service.write import create_mini_training_service
from education_group.tests.factories.factories.command import CreateOrphanMiniTrainingCommandFactory


class TestCreateOprhanMiniTraining(TestCase):
    def setUp(self):
        self.command = CreateOrphanMiniTrainingCommandFactory()

    @mock.patch('education_group.publisher.mini_training_created', autospec=True)
    @mock.patch("education_group.ddd.service.write.create_mini_training_service.MiniTrainingRepository.create")
    def test_should_return_mini_training_identity(self, mock_repository_create, mock_publisher):
        mock_repository_create.return_value = mini_training.MiniTrainingIdentity(
            code=self.command.code,
            year=self.command.start_year
        )
        result = create_mini_training_service.create_orphan_mini_training(self.command)
        self.assertEqual(
            result,
            mini_training.MiniTrainingIdentity(code=self.command.code, year=self.command.start_year)
        )
        self.assertTrue(mock_publisher.send.called)

