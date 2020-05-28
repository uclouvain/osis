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
from typing import Type
from unittest import mock
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils.translation import gettext as _

import program_management.ddd.command
import program_management.ddd.service.write.paste_element_service
from base.ddd.utils import business_validator
from base.ddd.utils.validation_message import MessageLevel, BusinessValidationMessage, BusinessValidationMessageList
from base.models.enums.education_group_types import TrainingType
from program_management.ddd.domain import program_tree, node
from program_management.ddd.service import attach_node_service
from program_management.ddd.service.write import paste_element_service
from program_management.ddd.validators import _validate_end_date_and_option_finality
from program_management.ddd.validators._infinite_recursivity import InfiniteRecursivityTreeValidator
from program_management.ddd.validators._minimum_editable_year import MinimumEditableYearValidator
from program_management.ddd.validators.link import CreateLinkValidatorList
from program_management.ddd.validators.validators_by_business_action import PasteNodeValidatorList
from program_management.models.enums.node_type import NodeType
from program_management.tests.ddd.factories.commands.paste_element_command import PasteElementCommandFactory
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeEducationGroupYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.service.mixins import ValidatorPatcherMixin


class TestPasteNode(SimpleTestCase, ValidatorPatcherMixin):

    def setUp(self):
        self.root_node = NodeEducationGroupYearFactory(node_type=TrainingType.BACHELOR)
        self.tree = ProgramTreeFactory(root_node=self.root_node)
        self.node_to_paste = NodeEducationGroupYearFactory()
        self.node_to_paste_type = NodeType.EDUCATION_GROUP

        self._patch_persist_tree()
        self._patch_load_tree()
        self._patch_load_child_node_to_attach()
        self.paste_command = PasteElementCommandFactory(
            root_id=self.tree.root_node.node_id,
            node_to_paste_id=self.node_to_paste.node_id,
            node_to_paste_type=self.node_to_paste_type,
        )

    def _patch_persist_tree(self):
        patcher_persist = patch("program_management.ddd.repositories.persist_tree.persist")
        self.addCleanup(patcher_persist.stop)
        self.mock_persist = patcher_persist.start()

    def _patch_load_tree(self):
        patcher_load = patch("program_management.ddd.repositories.load_tree.load")
        self.addCleanup(patcher_load.stop)
        self.mock_load = patcher_load.start()
        self.mock_load.return_value = self.tree

    def _patch_load_child_node_to_attach(self):
        patcher_load = patch("program_management.ddd.repositories.load_node.load_by_type")
        self.addCleanup(patcher_load.stop)
        self.mock_load = patcher_load.start()
        self.mock_load.return_value = self.node_to_paste

    @patch.object(program_tree.ProgramTree, 'paste_node')
    def test_should_return_node_identity_attached_when_paste_was_successful(self, mock_attach_node):
        mock_attach_node.return_value = None
        result = program_management.ddd.service.write.paste_element_service.paste_element_service(self.paste_command)
        expected_result = node.NodeIdentity(code=self.node_to_paste.code, year=self.node_to_paste.year)

        self.assertEqual(result, expected_result)

    @patch.object(program_tree.ProgramTree, 'paste_node')
    def test_should_propagate_exception_when_paste_raises_one(self, mock_attach_node):
        mock_attach_node.side_effect = business_validator.BusinessExceptions(["error_message_text"])

        with self.assertRaises(business_validator.BusinessExceptions):
            program_management.ddd.service.write.paste_element_service.paste_element_service(self.paste_command)

    def test_when_commit_is_true_then_persist_modification(self):
        self.mock_validator(PasteNodeValidatorList, [_('Success message')], level=MessageLevel.SUCCESS)
        paste_command_with_commit_set_to_true = PasteElementCommandFactory(
            root_id=self.tree.root_node.node_id,
            node_to_paste_id=self.node_to_paste.node_id,
            node_to_paste_type=self.node_to_paste_type,
            commit=True
        )
        paste_element_service.paste_element_service(paste_command_with_commit_set_to_true)
        self.assertTrue(self.mock_persist.called)

    def test_when_commit_is_false_then_should_not_persist_modification(self):
        self.mock_validator(PasteNodeValidatorList, [_('Success message')], level=MessageLevel.SUCCESS)
        program_management.ddd.service.write.paste_element_service.paste_element_service(self.paste_command)
        self.assertFalse(self.mock_persist.called)

    @mock.patch("program_management.ddd.service.detach_node_service.detach_node")
    def test_when_path_to_detach_is_set_then_should_call_detach_service(self, mock_detach):
        mock_detach.return_value = BusinessValidationMessageList([])
        self.mock_validator(PasteNodeValidatorList, [_('Success message')], level=MessageLevel.SUCCESS)
        paste_command_with_path_to_detach_set = PasteElementCommandFactory(
            root_id=self.tree.root_node.node_id,
            node_to_paste_id=self.node_to_paste.node_id,
            node_to_paste_type=self.node_to_paste_type,
            path_where_to_detach="a|b"
        )
        paste_element_service.paste_element_service(paste_command_with_path_to_detach_set)
        self.assertTrue(mock_detach.called)


class TestCheckAttach(SimpleTestCase, ValidatorPatcherMixin):
    def setUp(self) -> None:
        self.tree = ProgramTreeFactory()
        self.node_to_attach_from = NodeEducationGroupYearFactory()
        LinkFactory(parent=self.tree.root_node, child=self.node_to_attach_from)
        self.path = "|".join([str(self.tree.root_node.node_id), str(self.node_to_attach_from.node_id)])

        self.node_to_attach_1 = NodeEducationGroupYearFactory()
        self.node_to_attach_2 = NodeEducationGroupYearFactory()

        self._patch_load_tree()
        self._patch_load_node()
        self.mock_create_link_validator = self._patch_validator_is_valid(CreateLinkValidatorList)
        self.mock_minimum_year_editable = self._patch_validator_is_valid(MinimumEditableYearValidator)
        self.mock_infinite_recursivity_tree = self._patch_validator_is_valid(InfiniteRecursivityTreeValidator)
        self.mock_validate_end_date_and_option_finality = self._patch_validator_is_valid(
            _validate_end_date_and_option_finality.ValidateEndDateAndOptionFinality
        )

    def _patch_load_node(self):
        patcher_load_nodes = mock.patch(
            "program_management.ddd.repositories.load_node.load_by_type"
        )
        self.mock_load_node = patcher_load_nodes.start()
        self.mock_load_node.side_effect = [self.node_to_attach_1, self.node_to_attach_2]
        self.addCleanup(patcher_load_nodes.stop)

    def _patch_load_tree(self):
        patcher_load_tree = mock.patch(
            "program_management.ddd.repositories.load_tree.load"
        )
        self.mock_load_tree = patcher_load_tree.start()
        self.mock_load_tree.return_value = self.tree
        self.addCleanup(patcher_load_tree.stop)

    def _patch_validator_is_valid(self, validator_class: Type[business_validator.BusinessValidator]):
        patch_validator = mock.patch.object(
            validator_class, "is_valid"
        )
        mock_validator = patch_validator.start()
        mock_validator.return_value = True
        self.addCleanup(patch_validator.stop)
        return mock_validator

    def test_should_call_return_error_if_no_nodes_to_attach(self):
        check_command = program_management.ddd.command.CheckAttachNodeCommand(
            root_id=self.tree.root_node.node_id,
            nodes_to_attach=[],
            path_where_to_attach=self.path
        )
        result = attach_node_service.check_attach(check_command)
        self.assertIn(_("Please select an item before adding it"), result)

    def test_should_call_validate_end_date_and_option_finality(self):
        check_command = program_management.ddd.command.CheckAttachNodeCommand(
            root_id=self.tree.root_node.node_id,
            nodes_to_attach=[
                (self.node_to_attach_1.node_id, self.node_to_attach_1.node_type),
                (self.node_to_attach_2.node_id, self.node_to_attach_2.node_type)
            ],
            path_where_to_attach=self.path
        )
        attach_node_service.check_attach(check_command)

        self.assertEqual(self.mock_validate_end_date_and_option_finality.call_count, 2)

    def test_should_call_specific_validators(self):
        check_command = program_management.ddd.command.CheckAttachNodeCommand(
            root_id=self.tree.root_node.node_id,
            nodes_to_attach=[
                (self.node_to_attach_1.node_id, self.node_to_attach_1.node_type),
                (self.node_to_attach_2.node_id, self.node_to_attach_2.node_type)
            ],
            path_where_to_attach=self.path
        )
        attach_node_service.check_attach(check_command)

        self.assertEqual(self.mock_create_link_validator.call_count, 2)
        self.assertEqual(self.mock_minimum_year_editable.call_count, 2)
        self.assertEqual(self.mock_infinite_recursivity_tree.call_count, 2)
