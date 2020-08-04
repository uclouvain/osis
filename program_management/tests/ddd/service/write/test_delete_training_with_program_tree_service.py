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

from education_group.ddd.domain import training, group
from program_management.ddd import command
from program_management.ddd.domain import program_tree_version, program_tree
from program_management.ddd.service.write import delete_training_with_program_tree_service


class TesteDeleteTrainingWithProgramTree(TestCase):
    @mock.patch("program_management.ddd.service.write.delete_standard_program_tree_version_service."
                "delete_standard_program_tree_version")
    def test_should_call_appropriate_delete_services(
            self,
            mock_delete_program_tree_version):

        mock_delete_program_tree_version.return_value = [
            program_tree_version.ProgramTreeVersionIdentity(
                offer_acronym='Acronym',
                version_name='',
                is_transition=False,
                year=2019
            )
        ]
        delete_command = command.DeleteTrainingWithProgramTreeCommand(
            code='Code',
            offer_acronym='Acronym',
            version_name='',
            is_transition=False,
            from_year=2019
        )
        result = delete_training_with_program_tree_service.delete_training_with_program_tree(delete_command)

        self.assertTrue(mock_delete_program_tree_version.called)
