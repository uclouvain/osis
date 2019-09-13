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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import collections

from django.test import TestCase

from base.business.education_groups.general_information_sections import SECTIONS_PER_OFFER_TYPE
from base.tests.factories.education_group_year import EducationGroupYearFactory, EducationGroupYearCommonFactory
from cms.enums.entity_name import OFFER_YEAR
from cms.tests.factories.translated_text import TranslatedTextFactory
from cms.tests.factories.translated_text_label import TranslatedTextLabelFactory
from education_group.api.serializers.general_information import GeneralInformationSerializer
from webservices.business import EVALUATION_KEY


class GeneralInformationSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.egy = EducationGroupYearFactory()
        common_egy = EducationGroupYearCommonFactory(academic_year=cls.egy.academic_year)
        cls.pertinent_sections = SECTIONS_PER_OFFER_TYPE[cls.egy.education_group_type.name]
        for section in cls.pertinent_sections['common']:
            TranslatedTextLabelFactory(
                language='en',
                text_label__label=section
            )
            TranslatedTextFactory(
                reference=common_egy.id,
                entity=OFFER_YEAR,
                language='en',
                text_label__label=section
            )
        for section in cls.pertinent_sections['specific']:
            TranslatedTextLabelFactory(
                language='en',
                text_label__label=section
            )
            TranslatedTextFactory(
                reference=cls.egy.id,
                entity=OFFER_YEAR,
                language='en',
                text_label__label=section
            )
        cls.serializer = GeneralInformationSerializer(cls.egy, context={'language': 'en'})

    def test_contains_expected_fields(self):
        expected_fields = [
            'language',
            'acronym',
            'title',
            'year',
            'sections'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_content_field_is_list_of_dict(self):
        expected_fields = [
            'id',
            'label',
            'content',
        ]
        self.assertEqual(type(self.serializer.data['sections']), list)
        self.assertEqual(
            len(self.serializer.data['sections']),
            len(self.pertinent_sections['common'] + self.pertinent_sections['specific']) - 1
            # EVALUATION SPECIFIC AND COMMON IN ONLY ONE ENTRY
        )
        for section in self.serializer.data['sections']:
            if section['id'] == EVALUATION_KEY:
                self.assertTrue(isinstance(section, dict))
                self.assertListEqual(list(section.keys()), expected_fields + ['free_text'])
            else:
                self.assertTrue(isinstance(section, collections.OrderedDict))
                self.assertListEqual(list(section.keys()), expected_fields)
