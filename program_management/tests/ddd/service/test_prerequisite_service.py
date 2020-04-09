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
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils.translation import gettext as _

from base.ddd.utils.validation_message import MessageLevel, BusinessValidationMessage
from base.models.enums.education_group_types import TrainingType
from program_management.ddd.domain import program_tree
from program_management.ddd.domain.program_tree import build_path
from program_management.ddd.service import detach_node_service, prerequisite_service
from program_management.ddd.validators._has_or_is_prerequisite import IsPrerequisiteValidator
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeEducationGroupYearFactory, NodeLearningUnitYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.service.mixins import ValidatorPatcherMixin


class TestCheckIsPrerequisiteInTreesUsingNode(SimpleTestCase, ValidatorPatcherMixin):

    def setUp(self):
        self.node_to_detach = NodeLearningUnitYearFactory()
        link1 = LinkFactory(child=self.node_to_detach)
        link2 = LinkFactory(child=self.node_to_detach)
        link3 = LinkFactory(child=self.node_to_detach)
        self.trees = [
            ProgramTreeFactory(root_node=link1.parent),
            ProgramTreeFactory(root_node=link2.parent),
            ProgramTreeFactory(root_node=link3.parent),
        ]

    @patch('program_management.ddd.repositories.load_tree.load_trees_from_children')
    def test_when_node_is_prerequisite_in_trees(self, mock_load):
        mock_load.return_value = self.trees

        self.mock_validator(IsPrerequisiteValidator, ['error is prerequisite'])

        result = prerequisite_service.check_is_prerequisite_in_trees_using_node(self.node_to_detach)
        assertion_msg = "Should have 3 errors, because the node is used in 3 programs where it is a prerequisite"
        self.assertEqual(result.messages.count('error is prerequisite'), 3, assertion_msg)

    @patch('program_management.ddd.repositories.load_tree.load_trees_from_children')
    def test_when_node_is_not_prerequisite_in_any_trees(self, mock_load):
        mock_load.return_value = self.trees

        self.mock_validator(IsPrerequisiteValidator, [])

        result = prerequisite_service.check_is_prerequisite_in_trees_using_node(self.node_to_detach)
        assertion_msg = "Should have any error, because the node is used in 3 programs without being a prerequisite"
        self.assertListEqual(result.messages, [], assertion_msg)
