##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.conf import settings
from django.test import TestCase, RequestFactory
from rest_framework.reverse import reverse

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import TrainingFactory
from education_group.api.serializers.learning_unit import EducationGroupRootsListSerializer


class EducationGroupRootsListSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.training = TrainingFactory(
            acronym='BIR1BA',
            partial_acronym='LBIR1000I',
            academic_year=cls.academic_year,
        )
        url = reverse('education_group_api_v1:training-detail', kwargs={'uuid': cls.training.uuid})
        cls.serializer = EducationGroupRootsListSerializer(cls.training, context={'request': RequestFactory().get(url)})

    def test_contains_expected_fields(self):
        expected_fields = [
            'url',
            'acronym',
            'credits',
            'decree_category',
            'decree_category_text',
            'duration',
            'duration_unit',
            'duration_unit_text',
            'education_group_type',
            'education_group_type_text',
            'title',
            'academic_year',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_academic_year_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['academic_year'],
            self.academic_year.year
        )

    def test_ensure_education_group_type_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['education_group_type'],
            self.training.education_group_type.name
        )

    def test_ensure_title_field_is_dict(self):
        expected_dict = {
            settings.LANGUAGE_CODE_FR[:2]: self.training.title,
            settings.LANGUAGE_CODE_EN: self.training.title_english
        }
        self.assertDictEqual(self.serializer.data['title'], expected_dict)
