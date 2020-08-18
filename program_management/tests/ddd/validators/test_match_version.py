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
from django.utils.translation import gettext as _

from program_management.ddd.validators._match_version import MatchVersionValidator
from program_management.tests.ddd.validators.mixins import TestValidatorValidateMixin


class TestMatchVersionValidator(TestValidatorValidateMixin, SimpleTestCase):

    def setUp(self):
        self.root_node_version_name = ''
        self.node_to_add_version_name = ''

    def test_should_not_raise_exception_when_versions_match(self):
        self.assertValidatorNotRaises(MatchVersionValidator(self.root_node_version_name, self.node_to_add_version_name))

    def test_should_raise_exception_when_versions_mismatch(self):
        self.node_to_add_version_name = 'TEST'
        expected_message = _(
            'The child version must be the same as the root node version'
        )
        self.assertValidatorRaises(
            MatchVersionValidator(self.root_node_version_name, self.node_to_add_version_name),
            [expected_message]
        )
