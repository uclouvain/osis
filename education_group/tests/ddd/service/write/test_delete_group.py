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
from education_group.ddd.domain import exception, group
from education_group.ddd.service.write import delete_group_service


class TestDeleteGroup(TestCase):
    @mock.patch("education_group.ddd.repository.group.GroupRepository", autospec=True)
    def test_delete_trainings(self, mock_group_repository):
        mock_group_repository.delete.side_effect = [None, None, exception.GroupNotFoundException]

        delete_command = command.DeleteGroupCommand(code="Code", from_year=2018)
        result = delete_group_service.delete_group(delete_command)

        self.assertListEqual(
            [
                group.GroupIdentity(code="Code", year=2018),
                group.GroupIdentity(code="Code", year=2019)
            ],
            result
        )
        self.assertEqual(3, mock_group_repository.delete.call_count)
