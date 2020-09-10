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

from education_group.tests.ddd.factories.command.update_training_factory import UpdateTrainingCommandFactory
from program_management.ddd.service.write import update_training_with_program_tree_service


class TestUpdateAndReportTrainingWithProgramTree(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cmd = UpdateTrainingCommandFactory(code="LDROI1200M", abbreviated_title="DROI2M", year=2018)

    def setUp(self):
        self.update_training_patcher = mock.patch(
            "program_management.ddd.service.write.update_training_with_program_tree_service."
            "update_training_service.update_training",
            return_value=[]
        )
        self.mocked_update_training = self.update_training_patcher.start()
        self.addCleanup(self.update_training_patcher.stop)

        self.update_group_patcher = mock.patch(
            "program_management.ddd.service.write.update_training_with_program_tree_service."
            "update_group_service.update_group",
            return_value=[]
        )
        self.mocked_update_group = self.update_group_patcher.start()
        self.addCleanup(self.update_group_patcher.stop)

        self.postpone_pgrm_tree_patcher = mock.patch(
            "program_management.ddd.service.write.update_training_with_program_tree_service."
            "postpone_program_tree_service.postpone_program_tree",
            return_value=[]
        )
        self.mocked_postpone_pgrm_tree = self.postpone_pgrm_tree_patcher.start()
        self.addCleanup(self.postpone_pgrm_tree_patcher.stop)

        self.postpone_pgrm_tree_version_patcher = mock.patch(
            "program_management.ddd.service.write.update_training_with_program_tree_service."
            "postpone_tree_version_service.postpone_program_tree_version",
            return_value=[]
        )
        self.mocked_postpone_pgrm_tree_version = self.postpone_pgrm_tree_version_patcher.start()
        self.addCleanup(self.postpone_pgrm_tree_version_patcher.stop)

    def test_assert_call_multiple_service(self):
        update_training_with_program_tree_service.update_and_report_training_with_program_tree(self.cmd)

        self.assertTrue(self.mocked_update_training.called)
        self.assertTrue(self.mocked_update_group.called)
        self.assertTrue(self.mocked_postpone_pgrm_tree.called)
        self.assertTrue(self.mocked_postpone_pgrm_tree_version.called)
