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
import uuid

from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from learning_unit.api.serializers.learning_unit import LearningUnitDetailedSerializer


class LearningUnitAttributionTestCase(APITestCase):
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
        cls.person = PersonFactory()
        cls.url = reverse('learning_unit_api_v1:learningunits_read', kwargs={'uuid': cls.luy.uuid})

    def setUp(self):
        self.client.force_authenticate(user=self.person.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_results_case_learning_unit_year_not_found(self):
        invalid_url = reverse('learning_unit_api_v1:learningunits_read', kwargs={'uuid': uuid.uuid4()})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_results(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = LearningUnitDetailedSerializer(self.luy, context={'request': RequestFactory().get(self.url)})

        self.assertEqual(response.data, serializer.data)
