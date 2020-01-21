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
from program_management.contrib.models import node
from program_management.contrib.models.education_group_program import EducationGroupProgram
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

    def test_create_education_group_program_ensure_links_are_correctly_saved(self):
        pass
