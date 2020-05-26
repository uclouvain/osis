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
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils.translation import gettext as _

from base.ddd.utils.validation_message import MessageLevel
from base.models.enums.education_group_types import TrainingType
from program_management.ddd.validators import _validate_end_date_and_option_finality
from program_management.ddd.validators._attach_finality_end_date import AttachFinalityEndDateValidator
from program_management.ddd.validators._attach_option import AttachOptionsValidator
from program_management.tests.ddd.factories.node import NodeGroupYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.service.mixins import ValidatorPatcherMixin


class TestValidateEndDateAndOptionFinality(SimpleTestCase, ValidatorPatcherMixin):

    def setUp(self):
        self.root_node = NodeGroupYearFactory(node_type=TrainingType.PGRM_MASTER_120)
        self.tree_2m = ProgramTreeFactory(root_node=self.root_node)
        self.root_path = str(self.root_node.node_id)
        self.node_to_attach_not_finality = NodeGroupYearFactory(node_type=TrainingType.BACHELOR)

        self._patch_load_tree()

    def _patch_load_tree(self):
        patcher_load = patch("program_management.ddd.repositories.load_tree.load")
        self.addCleanup(patcher_load.stop)
        self.mock_load_tree_to_attach = patcher_load.start()
        self.mock_load_tree_to_attach.return_value = ProgramTreeFactory(root_node=self.node_to_attach_not_finality)

    @patch('program_management.ddd.repositories.load_tree.load_trees_from_children')
    def test_when_node_to_attach_is_not_finality(self, mock_load_2m_trees):
        """Unit test only for performance"""
        self.mock_validator(AttachFinalityEndDateValidator, [_('Success message')], level=MessageLevel.SUCCESS)

        validator = _validate_end_date_and_option_finality.ValidateEndDateAndOptionFinality(self.node_to_attach_not_finality)
        validator.is_valid()
        result = validator.messages
        self.assertFalse(mock_load_2m_trees.called)

    @patch('program_management.ddd.repositories.load_tree.load_trees_from_children')
    def test_when_end_date_of_finality_node_to_attach_is_not_valid(self, mock_load_2m_trees):
        mock_load_2m_trees.return_value = [self.tree_2m]
        node_to_attach = NodeGroupYearFactory(node_type=TrainingType.MASTER_MA_120)
        self.mock_load_tree_to_attach.return_value = ProgramTreeFactory(root_node=node_to_attach)
        self.mock_validator(AttachFinalityEndDateValidator, [_('Error end date finality message')])

        validator = _validate_end_date_and_option_finality.ValidateEndDateAndOptionFinality(node_to_attach)
        validator.is_valid()
        result = validator.messages
        validator_msg = "Error end date finality message"
        self.assertEqual(result[0].message, validator_msg)

    @patch('program_management.ddd.repositories.load_tree.load_trees_from_children')
    def test_when_end_date_of_finality_children_of_node_to_attach_is_not_valid(self, mock_load_2m_trees):
        mock_load_2m_trees.return_value = [self.tree_2m]
        not_finality = NodeGroupYearFactory(node_type=TrainingType.AGGREGATION)
        finality = NodeGroupYearFactory(node_type=TrainingType.MASTER_MA_120)
        not_finality.add_child(finality)
        self.mock_load_tree_to_attach.return_value = ProgramTreeFactory(root_node=not_finality)
        self.mock_validator(AttachFinalityEndDateValidator, [_('Error end date finality message')])

        validator = _validate_end_date_and_option_finality.ValidateEndDateAndOptionFinality(not_finality)
        validator.is_valid()
        result = validator.messages
        validator_msg = "Error end date finality message"
        self.assertEqual(result[0].message, validator_msg)

    @patch('program_management.ddd.repositories.load_tree.load_trees_from_children')
    def test_when_end_date_of_finality_node_to_attach_is_valid(self, mock_load_2m_trees):
        mock_load_2m_trees.return_value = [self.tree_2m]
        finality = NodeGroupYearFactory(node_type=TrainingType.MASTER_MA_120)
        self.mock_load_tree_to_attach.return_value = ProgramTreeFactory(root_node=finality)
        self.mock_validator(AttachFinalityEndDateValidator, [_('Success')], level=MessageLevel.SUCCESS)

        validator = _validate_end_date_and_option_finality.ValidateEndDateAndOptionFinality(finality)
        validator.is_valid()
        result = validator.messages
        self.assertEqual([], result)

    @patch('program_management.ddd.repositories.load_tree.load_trees_from_children')
    def test_when_option_validator_not_valid(self, mock_load_2m_trees):
        mock_load_2m_trees.return_value = [self.tree_2m]
        node_to_attach = NodeGroupYearFactory(node_type=TrainingType.MASTER_MA_120)
        self.mock_load_tree_to_attach.return_value = ProgramTreeFactory(root_node=node_to_attach)
        self.mock_validator(AttachOptionsValidator, [_('Error attach option message')])

        validator = _validate_end_date_and_option_finality.ValidateEndDateAndOptionFinality(node_to_attach)
        validator.is_valid()
        result = validator.messages
        validator_msg = "Error attach option message"
        self.assertIn(validator_msg, result)
