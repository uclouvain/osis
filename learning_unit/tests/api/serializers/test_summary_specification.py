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
from django.test import TestCase

from learning_unit.api.serializers.summary_specification import LearningUnitSummarySpecificationSerializer


class LearningAchievementListSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        data_to_serialize = {
            'bibliography': 'BIBLIO',
            'resume': 'RESUME',
            'evaluation_methods': 'EVALUATION',
            'other_informations': 'OTHER',
            'online_resources': 'ONLINE',
            'teaching_methods': 'TEACHING',
            'themes_discussed': 'THEMES',
            'prerequisite': 'PREREQUISITES',
            'mobility': 'MOBILITY',
            'teaching_methods_force_majeure': 'TEACHING_METHODS_FORCE_MAJEURE',
            'evaluation_methods_force_majeure': 'EVALUATION_METHODS_FORCE_MAJEURE',
            'other_informations_force_majeure': 'OTHER_INFORMATIONS_FORCE_MAJEURE'
         }
        cls.serializer = LearningUnitSummarySpecificationSerializer(data_to_serialize)

    def test_contains_expected_fields(self):
        expected_fields = [
            'bibliography',
            'resume',
            'evaluation_methods',
            'other_informations',
            'online_resources',
            'teaching_methods',
            'themes_discussed',
            'prerequisite',
            'mobility',
            'teaching_methods_force_majeure',
            'evaluation_methods_force_majeure',
            'other_informations_force_majeure',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)
