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
from django.test import TestCase

from program_management.ddd.contrib.validation import MessageLevel
from program_management.ddd.domain import node
from program_management.ddd.domain.node import Node, NodeGroupYear
from program_management.ddd.domain.program_tree import ProgramTree
from program_management.ddd.validators._validator_groups import AttachNodeValidatorList
from program_management.tests.ddd.factories.node import NodeGroupYearFactory
from program_management.tests.ddd.service.mixins import ValidatorPatcherMixin


class TestInitProgramTree(TestCase):
    def test_init_with_incorrect_instance_root_group(self):
        with self.assertRaises(Exception):
            ProgramTree(object)

    def test_init_set_correctly_instance_attribute(self):
        node = Node(0)
        tree = ProgramTree(node)

        self.assertEquals(tree.root_node, node)


class TestGetNodeProgramTree(TestCase):
    def setUp(self):
        self.subgroup_node = NodeGroupYear(1, "LTRONC100T", "Tronc commun", 2018)
        self.root_node = Node(0)
        self.root_node.add_child(self.subgroup_node)

        self.tree = ProgramTree(self.root_node)

    def test_get_node_case_invalid_path(self):
        with self.assertRaises(node.NodeNotFoundException):
            self.tree.get_node(path='dummy_path')

    def test_get_node_case_children_path(self):
        valid_path = "|".join([str(self.root_node.pk), str(self.subgroup_node.pk)])
        result_node = self.tree.get_node(path=valid_path)

        self.assertEquals(result_node.pk, self.subgroup_node.pk)

    def test_get_node_case_root_node_path(self):
        result_node = self.tree.get_node(path=str(self.root_node.pk))
        self.assertEquals(
            result_node.pk,
            self.root_node.pk
        )


class TestAttachNodeProgramTree(TestCase, ValidatorPatcherMixin):
    def setUp(self):
        root_node = NodeGroupYearFactory(node_id=0)
        self.tree = ProgramTree(root_node)

    def test_attach_node_case_no_path_specified(self):
        self.mock_validator(AttachNodeValidatorList, ['Success msg'], level=MessageLevel.SUCCESS)
        subgroup_node = NodeGroupYearFactory()
        self.tree.attach_node(subgroup_node)
        self.assertIn(subgroup_node, self.tree.root_node.children_as_nodes)

    def test_attach_node_case_path_specified_found(self):
        self.mock_validator(AttachNodeValidatorList, ['Success msg'], level=MessageLevel.SUCCESS)
        subgroup_node = NodeGroupYearFactory()
        self.tree.attach_node(subgroup_node)

        node_to_attach = NodeGroupYearFactory()
        path = "|".join([str(self.tree.root_node.pk), str(subgroup_node.pk)])
        self.tree.attach_node(node_to_attach, path=path)

        self.assertIn(node_to_attach, self.tree.get_node(path).children_as_nodes)

    def test_when_validator_list_is_valid(self):
        self.mock_validator(AttachNodeValidatorList, ['Success message text'], level=MessageLevel.SUCCESS)
        path = str(self.tree.root_node.node_id)
        child_to_attach = NodeGroupYearFactory()
        result = self.tree.attach_node(child_to_attach, path=path)
        self.assertEqual(result[0], 'Success message text')
        self.assertEqual(1, len(result))
        self.assertIn(child_to_attach, self.tree.root_node.children_as_nodes)

    def test_when_validator_list_is_not_valid(self):
        self.mock_validator(AttachNodeValidatorList, ['error message text'], level=MessageLevel.ERROR)
        path = str(self.tree.root_node.node_id)
        child_to_attach = NodeGroupYearFactory()
        result = self.tree.attach_node(child_to_attach, path=path)
        self.assertEqual(result[0], 'error message text')
        self.assertEqual(1, len(result))
        self.assertNotIn(child_to_attach, self.tree.root_node.children_as_nodes)


class TestDetachNodeProgramTree(TestCase):
    def setUp(self):
        self.leaf = NodeGroupYear(2, "LBRAF200G", "Sous groupe", 2018)
        self.common_core_node = NodeGroupYear(1, "LTRONC100T", "Tronc commun", 2018)
        self.root_node = NodeGroupYear(1, "LBIR1000A", "Bachelier en Bio", 2018)

        self.common_core_node.add_child(self.leaf)
        self.root_node.add_child(self.common_core_node)
        self.tree = ProgramTree(self.root_node)

    def test_detach_node_case_invalid_path(self):
        with self.assertRaises(node.NodeNotFoundException):
            self.tree.detach_node(path="dummy_path")

    def test_detach_node_case_valid_path(self):
        path_to_detach = "|".join([
            str(self.root_node.pk),
            str(self.common_core_node.pk),
            str(self.leaf.pk),
        ])

        self.tree.detach_node(path_to_detach)
        self.assertListEqual(
            self.tree.root_node.children[0].child.children,  # root_node/common_core
            []
        )

    def test_detach_node_case_try_to_detach_root_node(self):
        with self.assertRaises(Exception):
            self.tree.detach_node(str(self.root_node.pk))
