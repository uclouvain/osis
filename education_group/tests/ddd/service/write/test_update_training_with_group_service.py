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

from education_group.ddd.service.write import update_training_with_group_service
from education_group.tests.ddd.factories.command.update_training_factory import UpdateTrainingWithGroupCommandFactory
from education_group.tests.ddd.factories.training import TrainingIdentityFactory
from testing import mocks


class TestUpdateTrainingWithGroup(TestCase, mocks.MockPatcherMixin):
    def setUp(self) -> None:
        self.created_training_identites = [
            TrainingIdentityFactory(),
            TrainingIdentityFactory
        ]
        self.mock_update_training = self.mock_service(
            "education_group.ddd.service.write.update_training_service.update_training",
            return_value=self.created_training_identites
        )
        self.mock_update_group = self.mock_service(
            "education_group.ddd.service.write.update_group_service.update_group"
        )

    def test_should_call_update_training_service(self):
        update_command = UpdateTrainingWithGroupCommandFactory()

        update_training_with_group_service.update_training_with_group(update_command)

        self.assertTrue(self.mock_update_training.called)

    def test_should_call_update_group_service(self):
        update_command = UpdateTrainingWithGroupCommandFactory()

        update_training_with_group_service.update_training_with_group(update_command)

        self.assertTrue(self.mock_update_group.called)

    def test_should_return_training_identities(self):
        update_command = UpdateTrainingWithGroupCommandFactory()

        result = update_training_with_group_service.update_training_with_group(update_command)

        self.assertEqual(self.created_training_identites, result)
