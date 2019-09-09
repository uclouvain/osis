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

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.models.enums.education_group_types import GroupType
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import TrainingFactory, GroupFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from education_group.api.serializers.learning_unit import EducationGroupRootsListSerializer
from education_group.api.views.learning_unit import EducationGroupRootsList


class TrainingListSerializerTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
            BIR1BA
            |--Common Core
               |-- Learning Unit Year
        """
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.training = TrainingFactory(acronym='BIR1BA', partial_acronym='LBIR1000I', academic_year=cls.academic_year)
        cls.common_core = GroupFactory(
            education_group_type__name=GroupType.COMMON_CORE.name,
            academic_year=cls.academic_year
        )
        GroupElementYearFactory(parent=cls.training, child_branch=cls.common_core, child_leaf=None)

        cls.learning_unit_year = LearningUnitYearFactory(
            academic_year=cls.academic_year,
            learning_container_year__academic_year=cls.academic_year
        )
        GroupElementYearFactory(parent=cls.common_core, child_branch=None, child_leaf=cls.learning_unit_year)
        cls.person = PersonFactory()
        cls.url = reverse(
            'learning_unit_api_v1:' + EducationGroupRootsList.name,
            kwargs={'uuid': cls.learning_unit_year.uuid}
        )

    def setUp(self):
        self.client.force_authenticate(user=self.person.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete', 'put']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_results_case_learning_unit_year_not_found(self):
        invalid_url = reverse('learning_unit_api_v1:' + EducationGroupRootsList.name, kwargs={'uuid': uuid.uuid4()})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_results(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = EducationGroupRootsListSerializer([self.training], many=True)
        self.assertEqual(response.data, serializer.data)
