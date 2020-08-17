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
from django.test import SimpleTestCase

from program_management.ddd.validators import _program_tree_empty
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.validators.mixins import TestValidatorValidateMixin


class TestProgramTreeEmptyValidator(TestValidatorValidateMixin, SimpleTestCase):
    def test_should_not_raise_exception_when_program_tree_is_empty(self):
        emtpy_program_tree = ProgramTreeFactory()

        self.assertValidatorNotRaises(
            _program_tree_empty.ProgramTreeEmptyValidator(emtpy_program_tree),
        )

    def test_should_raise_exception_when_program_tree_is_empty(self):
        program_tree_with_content = ProgramTreeFactory()
        LinkFactory(parent=program_tree_with_content.root_node)

        self.assertValidatorRaises(
            _program_tree_empty.ProgramTreeEmptyValidator(program_tree_with_content),
            None
        )
