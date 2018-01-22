##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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

from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from base.models import proposal_learning_unit


class TestSearch(TestCase):
    def setUp(self):
        self.proposal_learning_unit = ProposalLearningUnitFactory()

    def test_find_by_learning_unit_year(self):
        a_proposal_learning_unit = proposal_learning_unit.find_by_learning_unit_year(
            self.proposal_learning_unit.learning_unit_year
        )
        self.assertEqual(a_proposal_learning_unit, self.proposal_learning_unit)

    def test_have_a_proposal(self):
        a_learning_unit_year = self.proposal_learning_unit.learning_unit_year
        self.assertTrue(proposal_learning_unit.have_a_proposal(a_learning_unit_year))

        self.proposal_learning_unit.delete()
        self.assertFalse(proposal_learning_unit.have_a_proposal(a_learning_unit_year))

    def test_find_by_folder(self):
        folder = self.proposal_learning_unit.folder
        self.assertTrue(proposal_learning_unit.find_by_folder(folder))

        self.proposal_learning_unit.delete()

        self.assertFalse(proposal_learning_unit.find_by_folder(folder))

