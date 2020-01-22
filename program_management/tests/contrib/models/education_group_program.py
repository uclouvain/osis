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

from base.models.group_element_year import GroupElementYear
from base.tests.factories.group_element_year import GroupElementYearFactory
from program_management.contrib import tree
from program_management.contrib.models import node
from program_management.contrib.models.education_group_program import EducationGroupProgram, NodeNotFoundException
from program_management.contrib.models.node import Node
from program_management.tests.factories.element import ElementEducationGroupYearFactory


class TestInitEducationGroupProgram(TestCase):
    def test_init_with_incorrect_instance_root_group(self):
        with self.assertRaises(Exception):
            EducationGroupProgram(object)

    def test_init_set_correctly_instance_attribute(self):
        node = Node()
        tree = EducationGroupProgram(node)

        self.assertEquals(tree.root_group, node)


class TestCreateEducationGroupProgram(TestCase):
    def setUp(self):
        self.training_node = node.factory.get_node(
            ElementEducationGroupYearFactory()
        )

    def test_create_education_group_program_ensure_no_save_when_no_children(self):
        tree = EducationGroupProgram(self.training_node)
        tree.save()

        self.assertEquals(GroupElementYear.objects.all().count(), 0)


class TestGetNodesEducationGroupProgram(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        root_node
        |-link_1_lvl_1--- A
                         |-link_1_lvl_2--- B
        |-link_2_lvl_1--- B

        :return:
        """
        cls.root_node = ElementEducationGroupYearFactory()
        cls.link_1_lvl_1 = GroupElementYearFactory(parent=cls.root_node.education_group_year)
        cls.link_1_lvl_2 = GroupElementYearFactory(parent=cls.link_1_lvl_1.child_branch)

        cls.link_1_lvl_2 = GroupElementYearFactory(
            parent=cls.root_node.education_group_year,
            child_branch=cls.link_1_lvl_2.child_branch
        )

    def setUp(self):
        self.tree = tree.fetch(self.root_node.education_group_year_id)  # TODO:  Replace to root_node.pk when migration is done

    def test_get_all_nodes_case_from_root_node(self):
        all_nodes = self.tree.get_all_nodes()

        self.assertIsInstance(all_nodes, list)
        self.assertEquals(len(all_nodes), 5)

    def test_get_specific_node_case_path_not_exist(self):
        with self.assertRaises(NodeNotFoundException):
            self.tree.get_node("dummy_path")

    def test_get_specific_node_case_path_exist(self):
        path = "|".join([str(self.link_1_lvl_1.parent_id), str(self.link_1_lvl_1.child_branch_id)])

        node = self.tree.get_node(path)
        self.assertEquals(node.pk, self.link_1_lvl_1.child_branch_id)
        self.assertEquals(node.acronym, self.link_1_lvl_1.child_branch.acronym)

