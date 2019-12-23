##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.core.exceptions import ValidationError
from django.test import TestCase

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.learning_class_year import LearningClassYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from education_group.tests.factories.group import GroupFactory
from education_group.tests.factories.group_year import GroupYearFactory
from program_management.models.element import Element
from program_management.tests.factories.element import ElementFactory, ElementEducationGroupYearFactory, \
    ElementLearningUnitYearFactory, ElementLearningClassYearFactory, ElementGroupYearFactory


class ElementTest(TestCase):

    def setUp(self):
        academic_yr = AcademicYearFactory(year=2020)
        self.egy = EducationGroupYearFactory(academic_year=academic_yr)
        self.luy = LearningUnitYearFactory(academic_year=academic_yr)
        lcpy = LearningComponentYearFactory(learning_unit_year=self.luy)
        self.lcy = LearningClassYearFactory(learning_component_year=lcpy)
        g = GroupFactory(start_year=academic_yr)
        self.gy = GroupYearFactory(group=g)

    def test_clean_no_foreign_key_set(self):
        element = ElementFactory()
        with self.assertRaises(ValidationError):
            element.clean()
            self.assertFalse(
                Element.objects.get(education_group_year=None,
                                    group_year=None,
                                    learning_unit_year=None,
                                    learning_class_year=None,).exists()
            )

    def test_clean_one_education_group_year_fk(self):
        element = ElementEducationGroupYearFactory.build(education_group_year=self.egy)
        element.clean()
        element.save()

        self.assertTrue(
            Element.objects.filter(education_group_year=element.education_group_year).exists()
        )

    def test_clean_one_group_year_fk(self):
        element = ElementGroupYearFactory.build(group_year=self.gy)
        element.clean()
        element.save()

        self.assertTrue(
            Element.objects.filter(group_year=self.gy).exists()
        )

    def test_clean_one_learning_unit_year_fk(self):
        element = ElementLearningUnitYearFactory.build(learning_unit_year=self.luy)
        element.clean()
        element.save()

        self.assertTrue(
            Element.objects.filter(learning_unit_year=self.luy).exists()
        )

    def test_clean_one_learning_class_year_fk(self):
        element = ElementLearningClassYearFactory.build(learning_class_year=self.lcy)
        element.clean()
        element.save()

        self.assertTrue(
            Element.objects.filter(learning_class_year=self.lcy).exists()
        )
