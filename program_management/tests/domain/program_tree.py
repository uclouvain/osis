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

from program_management.domain import node
from program_management.domain.node import Node, NodeGroupYear
from program_management.domain.program_tree import ProgramTree


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

    def test_get_node_case_valid_path(self):
        valid_path = "|".join([str(self.root_node.pk), str(self.subgroup_node.pk)])
        result_node = self.tree.get_node(path=valid_path)

        self.assertEquals(result_node.pk, self.subgroup_node.pk)


class TestAddNodeProgramTree(TestCase):
    def setUp(self):
        root_node = Node(0)
        self.tree = ProgramTree(root_node)

    def test_add_node_case_no_path_specified(self):
        subgroup_node = NodeGroupYear(1, "LTRONC100T", "Tronc commun", 2018)
        self.tree.add_node(subgroup_node)

        self.assertEquals(self.tree.root_node.children[0].child.pk, subgroup_node.pk)

    def test_add_node_case_path_specified_found(self):
        subgroup_node = NodeGroupYear(1, "LTRONC100T", "Tronc commun", 2018)
        self.tree.add_node(subgroup_node)

        node_to_add = NodeGroupYear(5, "LSUBG200G", "Sous groupe", 2018)
        path = "|".join([str(self.tree.root_node.pk), str(subgroup_node.pk)])
        self.tree.add_node(node_to_add, path=path)

        self.assertEquals(len(self.tree.get_node(path).children), 1)
        self.assertEquals(self.tree.get_node(path).children[0].child.pk, node_to_add.pk)
