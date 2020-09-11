##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import copy

from django.test import SimpleTestCase

from education_group.ddd.domain.exception import GroupCopyConsistencyException
from education_group.ddd.validators._copy_check_group_consistency import CheckGroupConsistencyValidator

from education_group.tests.ddd.factories.group import GroupFactory


class TestCheckGroupConsistencyValidator(SimpleTestCase):
    def test_assert_raise_exception_when_fields_are_different(self):
        group_from = GroupFactory()
        group_to = GroupFactory()

        validator = CheckGroupConsistencyValidator(group_from, group_to)
        with self.assertRaises(GroupCopyConsistencyException):
            validator.validate()

    def test_assert_return_true_when_identical(self):
        group_from = GroupFactory()
        group_to = copy.deepcopy(group_from)

        validator = CheckGroupConsistencyValidator(group_from, group_to)
        self.assertTrue(validator.validate())
