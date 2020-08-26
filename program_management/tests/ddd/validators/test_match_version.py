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
from mock import patch

from base.tests.factories.academic_year import AcademicYearFactory
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.ddd.validators._match_version import MatchVersionValidator
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory
from program_management.tests.ddd.validators.mixins import TestValidatorValidateMixin


class TestMatchVersionValidator(TestValidatorValidateMixin, SimpleTestCase):

    def setUp(self):
        self.academic_year = AcademicYearFactory.build(current=True)
        self.tree = ProgramTreeVersionFactory().tree
        self.node_to_attach = ProgramTreeVersionFactory().tree.root_node

    @patch(
        'program_management.ddd.domain.service.identity_search.ProgramTreeVersionIdentitySearch.get_from_node_identity',
    )
    def test_should_not_raise_exception_when_versions_match(self, mock_node_identity):
        identity_values = {'year': self.academic_year, 'version_name': '', 'is_transition': False}
        mock_node_identity.side_effect = [
            ProgramTreeVersionIdentity(offer_acronym=self.tree.root_node.code, **identity_values),
            ProgramTreeVersionIdentity(offer_acronym=self.node_to_attach.code, **identity_values)
        ]
        self.assertValidatorNotRaises(MatchVersionValidator(self.tree, self.node_to_attach))

    @patch(
        'program_management.ddd.domain.service.identity_search.ProgramTreeVersionIdentitySearch.get_from_node_identity',
    )
    def test_should_raise_exception_when_versions_mismatch(self, mock_node_identity):
        identity_values = {'year': self.academic_year, 'is_transition': False}
        mock_node_identity.side_effect = [
            ProgramTreeVersionIdentity(offer_acronym=self.tree.root_node.code, version_name='A', **identity_values),
            ProgramTreeVersionIdentity(offer_acronym=self.node_to_attach.code, version_name='B', **identity_values)
        ]
        expected_message = _(
            '%(node_to_add)s version must be the same as %(root_node)s version'
        ) % {
            'node_to_add': "{} - {}[{}]".format(self.node_to_attach.code, self.node_to_attach.code, 'B'),
            'root_node': "{} - {}[{}]".format(self.tree.root_node.code, self.tree.root_node.code, 'A')
        }

        self.assertValidatorRaises(
            MatchVersionValidator(self.tree, self.node_to_attach),
            [expected_message]
        )
