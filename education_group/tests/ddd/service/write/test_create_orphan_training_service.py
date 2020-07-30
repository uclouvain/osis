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
from education_group.tests.ddd.factories.training import TrainingFactory


class TestCreateAndPostponeOrphanTraining(TestCase):
    @mock.patch("education_group.ddd.service.write.postpone_training_service.postpone_training")
    @mock.patch("education_group.ddd.service.write.create_orphan_training_service.TrainingBuilder")
    @mock.patch("education_group.ddd.service.write.create_orphan_training_service.TrainingRepository")
    def test_should_return_as_many_identities_as_postponement_range(
            self,
            mock_repository,
            mock_builder,
            mock_postpone_training_service):
        source_training = TrainingFactory()
        postponed_trainings_identities = [
            training.TrainingIdentity(acronym="ACRONYM", year=2020),
            training.TrainingIdentity(acronym="ACRONYM", year=2021)
        ]
        mock_builder.return_value.get_training.return_value = source_training
        mock_repository.create.return_value = source_training.entity_id
        mock_postpone_training_service.return_value = postponed_trainings_identities

        cmd = CreateTrainingCommandFactory()
        result = create_orphan_training_service.create_and_postpone_orphan_training(cmd)

        self.assertListEqual(
            [source_training.entity_id] + postponed_trainings_identities,
            result
        )