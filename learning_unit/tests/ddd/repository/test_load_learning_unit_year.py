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

from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_component_year import LecturingLearningComponentYearFactory, \
    PracticalLearningComponentYearFactory
from learning_unit.ddd.repository.load_learning_unit_year import load_multiple


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
