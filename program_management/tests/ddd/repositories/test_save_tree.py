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
from base.tests.factories.academic_year import AcademicYearFactory
from program_management.ddd.repositories import save_tree
from program_management.tests.ddd.factories.node import NodeEducationGroupYearFactory, NodeLearningUnitYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory


class TestSaveTree(TestCase):
    def setUp(self):
        academic_year = AcademicYearFactory(current=True)

        self.root_node = NodeEducationGroupYearFactory(
            year=academic_year.year,
            create_django_objects_in_db=True
        )
        self.common_core_node = NodeEducationGroupYearFactory(
            year=academic_year.year,
            create_django_objects_in_db=True
        )
        self.learning_unit_year_node = NodeLearningUnitYearFactory(
            year=academic_year.year,
            create_django_objects_in_db=True
        )

    def test_case_tree_save_from_scratch(self):
        self.common_core_node.add_child(self.learning_unit_year_node)
        self.root_node.add_child(self.common_core_node)
        tree = ProgramTreeFactory(root_node=self.root_node)

        save_tree.save(tree)

        self.assertEquals(GroupElementYear.objects.all().count(), 2)

    def test_case_tree_save_with_some_existing_part(self):
        self.root_node.add_child(self.common_core_node)
        tree = ProgramTreeFactory(root_node=self.root_node)

        save_tree.save(tree)
        self.assertEquals(GroupElementYear.objects.all().count(), 1)

        # Append UE to common core
        self.common_core_node.add_child(self.learning_unit_year_node)
        save_tree.save(tree)
        self.assertEquals(GroupElementYear.objects.all().count(), 2)

    def test_case_tree_save_after_detach_element(self):
        self.root_node.add_child(self.common_core_node)
        tree = ProgramTreeFactory(root_node=self.root_node)

        save_tree.save(tree)
        self.assertEquals(GroupElementYear.objects.all().count(), 1)

        path_to_detach = "|".join([str(self.root_node.pk), str(self.common_core_node.pk)])
        tree.detach_node(path_to_detach)
        save_tree.save(tree)
        self.assertEquals(GroupElementYear.objects.all().count(), 0)
