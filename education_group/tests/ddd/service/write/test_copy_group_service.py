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

from education_group.ddd import command
from education_group.ddd.domain import group
from education_group.ddd.service.write import copy_group_service
from education_group.tests.ddd.factories.group import GroupFactory
from education_group.tests.ddd.factories.repository.group import get_fake_group_repository
from testing.mocks import MockPatcherMixin


class TestCopyGroup(TestCase, MockPatcherMixin):
    def setUp(self):
        self.group_2019 = GroupFactory(entity_identity__code="CODE", entity_identity__year=2019)
        self.group_2020 = GroupFactory(entity_identity__code="CODE", entity_identity__year=2020)
        self.groups = [self.group_2019, self.group_2020]

        self.fake_group_repo = get_fake_group_repository(self.groups)
        self.mock_repo("education_group.ddd.repository.group.GroupRepository", self.fake_group_repo)

    def test_should_return_entity_id_of_group_copied_to(self):
        copy_command = command.CopyGroupCommand(from_code="CODE", from_year=2019)

        result = copy_group_service.copy_group(copy_command)

        expected_entity_id = self.group_2020.entity_id
        self.assertEqual(expected_entity_id, result)

    def test_should_copy_values_to_next_year(self):
        copy_command = command.CopyGroupCommand(from_code="CODE", from_year=2019)

        result = copy_group_service.copy_group(copy_command)

        copy_group = self.fake_group_repo.get(self.group_2020.entity_id)

        self.assertTrue(copy_group.has_same_values_as(self.groups[0]))

    def test_should_create_a_new_group_when_next_year_copy_does_not_exist_year_in_repository(self):
        copy_command = command.CopyGroupCommand(from_code="CODE", from_year=2020)

        result = copy_group_service.copy_group(copy_command)

        expected_entity_id = group.GroupIdentity(code="CODE", year=2021)
        self.assertTrue(self.fake_group_repo.get(expected_entity_id))
