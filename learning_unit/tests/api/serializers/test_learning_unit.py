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
from django.test import TestCase, RequestFactory
from django.urls import reverse

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from learning_unit.api.serializers.learning_unit import LearningUnitDetailedSerializer


class LearningUnitDetailedSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        anac = AcademicYearFactory()
        requirement_entity = EntityFactory()
        EntityVersionFactory(
            start_date=AcademicYearFactory(year=anac.year - 1).start_date,
            end_date=AcademicYearFactory(year=anac.year + 1).end_date,
            entity=requirement_entity
        )
        cls.luy = LearningUnitYearFactory(
            academic_year=anac,
            learning_container_year__requirement_entity=requirement_entity
        )

        url = reverse('learning_unit_api_v1:learningunits_read', kwargs={'uuid': cls.luy.uuid})
        cls.serializer = LearningUnitDetailedSerializer(cls.luy, context={'request': RequestFactory().get(url)})

    def test_contains_expected_fields(self):
        expected_fields = [
            'url',
            'acronym',
            'academic_year',
            'credits',
            'requirement_entity',
            'status',
            'quadrimester',
            'quadrimester_text',
            'periodicity',
            'periodicity_text',
            'campus',
            'team',
            'language',
            'components',
            'parent',
            'partims'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)
