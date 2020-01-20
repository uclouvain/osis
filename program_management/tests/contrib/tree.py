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

from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from program_management.contrib import tree, node
from program_management.models.element import Element
from program_management.tests.factories.element import ElementEducationGroupYearFactory


class TestFetchTree(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_node = ElementEducationGroupYearFactory()
        cls.link_level_1 = GroupElementYearFactory(parent=cls.root_node)
        cls.link_level_2 = GroupElementYearFactory(
            parent=cls.link_level_1.child_branch,
            child_leaf=LearningUnitYearFactory()
        )

    def test_case_tree_root_not_exist(self):
        unknown_tree_root_id = -1
        with self.assertRaises(Element.DoesNotExist):
            tree.fetch(unknown_tree_root_id)

    def test_case_tree_root_with_multiple_level(self):
        education_group_program_tree = tree.fetch(self.root_node.pk)
        self.assertIsInstance(education_group_program_tree, tree.EducationGroupProgram)

        self.assertIsInstance(education_group_program_tree.root_group, node.NodeEductionGroupYear)
        self.assertEqual(len(education_group_program_tree.root_group.children), 1)
