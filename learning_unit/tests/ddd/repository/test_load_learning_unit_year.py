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

from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_component_year import LecturingLearningComponentYearFactory, \
    PracticalLearningComponentYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from learning_unit.ddd.repository.load_learning_unit_year import load_multiple
from learning_unit.ddd.repository import load_learning_unit_year


class TestLoadLearningUnitVolumes(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.l_unit_1 = LearningUnitYearFactory()
        cls.practical_volume = PracticalLearningComponentYearFactory(learning_unit_year=cls.l_unit_1,
                                                                     hourly_volume_total_annual=20,
                                                                     hourly_volume_partial_q1=15,
                                                                     hourly_volume_partial_q2=5,
                                                                     planned_classes=1
                                                                     )
        cls.lecturing_volume = LecturingLearningComponentYearFactory(learning_unit_year=cls.l_unit_1,
                                                                     hourly_volume_total_annual=40,
                                                                     hourly_volume_partial_q1=20,
                                                                     hourly_volume_partial_q2=20,
                                                                     planned_classes=2
                                                                     )

    def test_load_learning_unit_year_init_volumes(self):
        results = load_multiple([self.l_unit_1.id])

        self._assert_volume(results[0].practical_volume, self.practical_volume)
        self._assert_volume(results[0].lecturing_volume, self.lecturing_volume)

    def _assert_volume(self, volumes, expected):
        self.assertEqual(volumes.total_annual, expected.hourly_volume_total_annual)
        self.assertEqual(volumes.first_quadrimester, expected.hourly_volume_partial_q1)
        self.assertEqual(volumes.second_quadrimester, expected.hourly_volume_partial_q2)
        self.assertEqual(volumes.classes_count, expected.planned_classes)


class TestLoadLearningUnitEntities(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.academic_year = create_current_academic_year()

        cls.requirement_entity_version = EntityVersionFactory(acronym='DRT',
                                                              start_date=cls.academic_year.start_date)
        cls.allocation_entity_version = EntityVersionFactory(acronym='FIAL',
                                                             start_date=cls.academic_year.start_date)
        cls.l_unit_1 = LearningUnitYearFactory(
            academic_year=cls.academic_year,
            learning_container_year__academic_year=cls.academic_year,
            learning_container_year__requirement_entity=cls.requirement_entity_version.entity,
            learning_container_year__allocation_entity=cls.allocation_entity_version.entity,
        )

    def test_load_learning_unit_year_init_entities(self):
        results = load_multiple([self.l_unit_1.id])
        self.assertEqual(results[0].entities.requirement_entity_acronym, self.requirement_entity_version.acronym)
        self.assertEqual(results[0].entities.allocation_entity_acronym, self.allocation_entity_version.acronym)


class TestLoadLearningUnitProposal(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.academic_year = create_current_academic_year()

        cls.l_unit_1 = LearningUnitYearFactory()
        cls.proposal = ProposalLearningUnitFactory(learning_unit_year=cls.l_unit_1)

    def test_load_learning_unit_year_init_entities(self):
        results = load_multiple([self.l_unit_1.id])
        self.assertEqual(results[0].proposal.type, self.proposal.type)
        self.assertEqual(results[0].proposal.state, self.proposal.state)


class TestConvertStringToEnum(TestCase):

    def test_convert_quadrimester(self):
        self.assertIsNone(load_learning_unit_year.__convert_string_to_enum({'quadrimester': None}))
        self.assertIsNone(load_learning_unit_year.__convert_string_to_enum({}))
