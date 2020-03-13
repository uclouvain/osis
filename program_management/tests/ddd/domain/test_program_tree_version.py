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
from django.test import SimpleTestCase

from program_management.ddd.domain.program_tree_version import ProgramTreeVersion, ProgramTree
from program_management.tests.ddd.factories.node import NodeGroupYearFactory


class TestInit(SimpleTestCase):
    def setUp(self):
        self.root = NodeGroupYearFactory()

    def test_instance_type(self):
        obj = ProgramTreeVersion(root_node=self.root)
        self.assertIsInstance(obj, ProgramTree)

    def test_default_version_name_value(self):
        obj = ProgramTreeVersion(root_node=self.root)
        error_msg = "By default, a tree version instance is a 'Standard' version, identified by an empty name."
        self.assertEqual(obj.version_name, '', error_msg)

    def test_default_transition_value(self):
        obj = ProgramTreeVersion(root_node=self.root)
        error_msg = "By default, a tree version instance is not a transition program."
        self.assertFalse(obj.is_transition, error_msg)
