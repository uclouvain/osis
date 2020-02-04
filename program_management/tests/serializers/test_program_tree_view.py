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

from program_management.DomainDrivenDesign.domain.node import NodeGroupYear, NodeLearningUnitYear
from program_management.DomainDrivenDesign.domain.program_tree import ProgramTree
from program_management.serializers.program_tree_view import ProgramTreeViewSerializer


class TestProgramTreeViewSerializer(TestCase):
    def setUp(self):
        """
        root_node
        |-----common_core
             |---- LDROI100A (UE)
        |----subgroup1
             |---- LDROI120B (UE)
             |----subgroup2
                  |---- LDROI100A (UE)
        :return:
        """
        self.root_node = NodeGroupYear(1, "LBIR100B", "Bachelier en droit", 2018)
        self.common_core = NodeGroupYear(2, "LGROUP100A", "Tronc commun", 2018)
        self.ldroi100a = NodeLearningUnitYear(3, "LDROI100A", "Introduction", 2018)
        self.ldroi120b = NodeLearningUnitYear(4, "LDROI120B", "Séminaire", 2018)
        self.subgroup1 = NodeGroupYear(5, "LSUBGR100G", "Sous-groupe 1", 2018)
        self.subgroup2 = NodeGroupYear(6, "LSUBGR150G", "Sous-groupe 2", 2018)

        self.root_node.add_child(self.common_core)
        self.common_core.add_child(self.ldroi100a)
        self.root_node.add_child(self.subgroup1)
        self.subgroup1.add_child(self.ldroi120b)
        self.subgroup1.add_child(self.subgroup2)
        self.subgroup2.add_child(self.ldroi100a)
        self.tree = ProgramTree(root_node=self.root_node)

    def test_serialize_program_tree_ensure_context_have_root_keys(self):
        serializer = ProgramTreeViewSerializer(self.tree)
        self.assertEquals(serializer.context['root'], self.tree.root_node)

    def test_serialize_program_tree_assert_keys_of_root_element(self):
        serializer = ProgramTreeViewSerializer(self.tree)
        expected_keys = ['text', 'icon', 'children']

        self.assertListEqual(list(serializer.data.keys()), expected_keys)

    def test_serialize_program_tree_assert_node_child_element(self):
        serializer = ProgramTreeViewSerializer(self.tree)

        self.assertIsInstance(serializer.data['children'], list)
        self.assertEquals(
            serializer.data['children'][0]['path'],
            "|".join([str(self.root_node.pk), str(self.common_core.pk)]),
        )
        self.assertEquals(serializer.data['children'][0]['text'], self.common_core.acronym)
        self.assertEquals(serializer.data['children'][0]['icon'], None)
        self.assertIsInstance(serializer.data['children'][0]['children'], list)

    def test_serialize_program_tree_assert_keys_of_node_a_attr(self):
        serializer = ProgramTreeViewSerializer(self.tree)
        expected_keys = [
            "href", "root", "element_id", "element_type", "title", "attach_url", "detach_url",
            "modify_url", "attach_disabled", "attach_msg", "detach_disabled", "detach_msg", "modification_disabled",
            "modification_msg", "search_url"
        ]

        a_attr = serializer.data['children'][0]['a_attr']
        self.assertIsInstance(a_attr, dict)
        self.assertListEqual(list(a_attr.keys()), expected_keys)
