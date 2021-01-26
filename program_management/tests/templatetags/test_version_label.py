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

from program_management.templatetags.version_label import version_label
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionIdentityFactory


class TestVersionLabel(SimpleTestCase):
    def test_version_label(self):
        version_identity = ProgramTreeVersionIdentityFactory()
        expected_result = version_identity.version_name
        result = version_label(version_identity)
        self.assertEqual(result, expected_result)

    def test_version_label_transition(self):
        version_identity = ProgramTreeVersionIdentityFactory(is_transition=True, version_name='')
        expected_result = 'Transition'
        result = version_label(version_identity)
        self.assertEqual(result, expected_result)

    def test_version_label_specific_transition(self):
        version_identity = ProgramTreeVersionIdentityFactory(is_transition=True, version_name='TEST')
        expected_result = '{} - Transition'.format(version_identity.version_name)
        result = version_label(version_identity)
        self.assertEqual(result, expected_result)


class TestVersionLabelOnlySuffix(SimpleTestCase):
    def test_version_label(self):
        version_identity = ProgramTreeVersionIdentityFactory()
        expected_result = ""
        result = version_label(version_identity, only_suffix=True)
        self.assertEqual(result, expected_result)

    def test_version_label_transition(self):
        version_identity = ProgramTreeVersionIdentityFactory(is_transition=True, version_name='')
        expected_result = 'Transition'
        result = version_label(version_identity, only_suffix=True)
        self.assertEqual(result, expected_result)

    def test_version_label_specific_transition(self):
        version_identity = ProgramTreeVersionIdentityFactory(is_transition=True, version_name='TEST')
        expected_result = ' - Transition'
        result = version_label(version_identity, only_suffix=True)
        self.assertEqual(result, expected_result)
