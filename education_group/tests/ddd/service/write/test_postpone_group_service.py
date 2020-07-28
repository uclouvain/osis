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

from base.tests.factories.academic_year import AcademicYearFactory
from education_group.ddd import command
from education_group.ddd.domain import training, group
from education_group.ddd.service.write import postpone_training_service, postpone_group_service
from education_group.tests.ddd.factories.group import GroupFactory
from education_group.tests.ddd.factories.training import TrainingFactory


class TestPostponeGroup(TestCase):

    @classmethod
    def setUpTestData(cls):
        AcademicYearFactory(year=2018)
        AcademicYearFactory(year=2019)
        AcademicYearFactory(year=2020)

    @mock.patch("education_group.ddd.service.write.copy_group_service.copy_group")
    def test_should_return_a_number_of_identities_equal_to_difference_of_from_year_and_until_year(
            self,
            mock_copy_group_to_next_year_service,
    ):
        existing_group = GroupFactory(
            entity_identity=group.GroupIdentity(code="CODE", year=2018),
            end_year=2020
        )
        group_identities = [
            existing_group.entity_id,
            group.GroupIdentity(code="CODE", year=2019),
            group.GroupIdentity(code="CODE", year=2020)
        ]
        mock_copy_group_to_next_year_service.return_value = group_identities

        cmd = command.PostponeGroupCommand(code="CODE", postpone_from_year=2018, postpone_until_year=2020)
        result = postpone_group_service.postpone_group(cmd)

        self.assertListEqual(group_identities, result)
