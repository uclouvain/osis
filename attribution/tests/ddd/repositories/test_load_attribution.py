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

from attribution.ddd.domain.attribution import Attribution
from attribution.ddd.repositories.load_attribution import load_learning_unit_year_attributions
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.models.enums import learning_unit_year_subtypes
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory


class TestLoadAttribution(TestCase):

    @classmethod
    def setUpTestData(cls):
        academic_year = AcademicYearFactory(current=True)
        cls.l_unit_1 = LearningUnitYearFactory(
            acronym="LBIR1212",
            academic_year=academic_year,
            subtype=learning_unit_year_subtypes.FULL
        )
        component = LearningComponentYearFactory(learning_unit_year=cls.l_unit_1)

        cls.attribution_charge_news = _build_attributions(component)

        cls.l_unit_no_attribution = LearningUnitYearFactory(
            acronym="LBIR1213",
            academic_year=academic_year,
            subtype=learning_unit_year_subtypes.FULL
        )

    def test_load_learning_unit_year_attributions_number_of_attributions(self):
        results = load_learning_unit_year_attributions(self.l_unit_1.id)
        self.assertEqual(len(results), 2)

    def test_load_learning_unit_year_attributions_no_results(self):
        results = load_learning_unit_year_attributions(self.l_unit_no_attribution.id)
        self.assertEqual(len(results), 0)

    def test_load_learning_unit_year_attributions_content_and_order(self):
        results = load_learning_unit_year_attributions(self.l_unit_1.id)
        for obj in results:
            self.assertTrue(isinstance(obj, Attribution))

        self.assertEqual(results[0].teacher_last_name, "Marchal")
        self.assertEqual(results[0].teacher_first_name, "Cali")
        self.assertIsNone(results[0].teacher_middle_name)
        self.assertEqual(results[0].teacher_email, "cali@gmail.com")

        self.assertEqual(results[1].teacher_last_name, "Marchal")
        self.assertEqual(results[1].teacher_first_name, "Tilia")
        self.assertIsNone(results[1].teacher_middle_name)
        self.assertEqual(results[1].teacher_email, "tilia@gmail.com")


def _build_attributions(component):
    attribution_1 = AttributionChargeNewFactory(learning_component_year=component,
                                                attribution__tutor__person__last_name='Marchal',
                                                attribution__tutor__person__first_name='Tilia',
                                                attribution__tutor__person__email='tilia@gmail.com')
    attribution_2 = AttributionChargeNewFactory(learning_component_year=component,
                                                attribution__tutor__person__last_name='Marchal',
                                                attribution__tutor__person__first_name='Cali',
                                                attribution__tutor__person__email='cali@gmail.com')
    return [attribution_1, attribution_2]
