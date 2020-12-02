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
from django.conf import settings
from django.db.models import Value, IntegerField
from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import GroupType, TrainingType
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.education_group_year import TrainingFactory, EducationGroupYearMasterFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.prerequisite import PrerequisiteFactory
from base.tests.factories.prerequisite_item import PrerequisiteItemFactory
from base.tests.factories.user import UserFactory
from education_group.api.serializers.learning_unit import EducationGroupRootsListSerializer, \
    LearningUnitYearPrerequisitesListSerializer
from education_group.api.views.learning_unit import EducationGroupRootsList, LearningUnitPrerequisitesList
from education_group.tests.factories.group_year import GroupYearFactory
from program_management.models.education_group_version import EducationGroupVersion
from program_management.tests.factories.education_group_version import StandardEducationGroupVersionFactory
from program_management.tests.factories.element import ElementFactory

LEARNING_UNIT_API_HEAD = 'learning_unit_api_v1:'


class FilterEducationGroupRootsTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

        cls.academic_year = create_current_academic_year()

        cls.training = EducationGroupYearMasterFactory(
            academic_year=cls.academic_year, acronym='test2m', partial_acronym='test2m'
        )
        cls.group = GroupYearFactory(
            education_group_type__name=TrainingType.PGRM_MASTER_120.name,
            acronym='test2m', partial_acronym='test2m', academic_year=cls.academic_year
        )
        cls.version = StandardEducationGroupVersionFactory(root_group=cls.group, offer=cls.training)

        cls.common_core = GroupYearFactory(
            education_group_type__name=GroupType.COMMON_CORE.name,
            academic_year=cls.academic_year
        )
        common_core_element = ElementFactory(group_year=cls.common_core)
        GroupElementYearFactory(parent_element__group_year=cls.group, child_element=common_core_element)

        cls.training_2 = TrainingFactory(academic_year=cls.academic_year)
        group_2 = GroupYearFactory(
            education_group_type=cls.training_2.education_group_type,
            acronym=cls.training_2.acronym, partial_acronym=cls.training_2.partial_acronym,
            academic_year=cls.academic_year
        )
        StandardEducationGroupVersionFactory(root_group=group_2, offer=cls.training_2)

        cls.complementary_module = GroupYearFactory(
            education_group_type__name=GroupType.COMPLEMENTARY_MODULE.name,
            academic_year=cls.academic_year
        )
        complementary_module_element = ElementFactory(group_year=cls.complementary_module)
        GroupElementYearFactory(parent_element__group_year=group_2, child_element=complementary_module_element)

        cls.learning_unit_year = LearningUnitYearFactory(
            academic_year=cls.academic_year,
            learning_container_year__academic_year=cls.academic_year
        )
        cls.luy_element = ElementFactory(learning_unit_year=cls.learning_unit_year)
        gey = GroupElementYearFactory(
            parent_element=common_core_element,
            child_element=cls.luy_element
        )
        GroupElementYearFactory(
            parent_element=complementary_module_element,
            child_element=cls.luy_element
        )
        cls.annotated_version = EducationGroupVersion.objects.filter(id=cls.version.id).annotate(
            relative_credits=Value(gey.relative_credits, output_field=IntegerField())
        ).first()
        url_kwargs = {
            'acronym': cls.learning_unit_year.acronym,
            'year': cls.learning_unit_year.academic_year.year
        }
        cls.url = reverse(LEARNING_UNIT_API_HEAD + EducationGroupRootsList.name, kwargs=url_kwargs)

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_educationgrouproots_case_filter_ignore_complementary_module_params(self):
        query_string = {'ignore_complementary_module': 'true'}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = EducationGroupRootsListSerializer(
            [self.annotated_version],
            many=True,
            context={
                'request': RequestFactory().get(self.url),
                'language': settings.LANGUAGE_CODE_FR,
                'learning_unit_year': self.learning_unit_year
            }
        )
        self.assertEqual(response.data, serializer.data)

    def test_get_finality_root_and_not_itself(self):
        finality_root = EducationGroupYearMasterFactory(academic_year=self.academic_year)
        finality_root_group = GroupYearFactory(
            acronym=finality_root.acronym, partial_acronym=finality_root.partial_acronym,
            academic_year=self.academic_year,
            education_group_type=finality_root.education_group_type
        )
        finality_root_version = StandardEducationGroupVersionFactory(root_group=finality_root_group,
                                                                     offer=finality_root)

        finality = GroupYearFactory(
            academic_year=self.academic_year,
            education_group_type__name=TrainingType.MASTER_MD_120.name
        )
        finality_element = ElementFactory(group_year=finality)

        GroupElementYearFactory(parent_element__group_year=finality_root_group, child_element=finality_element)
        gey = GroupElementYearFactory(parent_element=finality_element, child_element=self.luy_element)
        annotated_finality = EducationGroupVersion.objects.filter(id=finality_root_version.id).annotate(
            relative_credits=Value(gey.relative_credits, output_field=IntegerField())
        ).first()
        query_string = {'ignore_complementary_module': 'true'}
        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = EducationGroupRootsListSerializer(
            [self.annotated_version, annotated_finality],
            many=True,
            context={
                'request': RequestFactory().get(self.url),
                'language': settings.LANGUAGE_CODE_FR,
                'learning_unit_year': self.learning_unit_year
            }
        )
        self.assertCountEqual(response.data, serializer.data)


class EducationGroupRootsListTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
            BIR1BA
            |--Common Core
               |-- Learning Unit Year
        """
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.training = TrainingFactory(
            education_group_type__name=TrainingType.BACHELOR.name,
            acronym='BIR1BA', partial_acronym='LBIR1000I', academic_year=cls.academic_year
        )
        cls.group = GroupYearFactory(
            education_group_type__name=TrainingType.BACHELOR.name,
            acronym='BIR1BA', partial_acronym='LBIR1000I', academic_year=cls.academic_year
        )
        cls.version = StandardEducationGroupVersionFactory(root_group=cls.group, offer=cls.training)
        cls.common_core = GroupYearFactory(
            education_group_type__name=GroupType.COMMON_CORE.name,
            academic_year=cls.academic_year
        )
        common_core_element = ElementFactory(group_year=cls.common_core)
        GroupElementYearFactory(parent_element__group_year=cls.group, child_element=common_core_element)

        cls.learning_unit_year = LearningUnitYearFactory(
            academic_year=cls.academic_year,
            learning_container_year__academic_year=cls.academic_year
        )
        luy_element = ElementFactory(learning_unit_year=cls.learning_unit_year)
        gey = GroupElementYearFactory(
            parent_element=common_core_element,
            child_element=luy_element
        )
        cls.annotated_version = EducationGroupVersion.objects.filter(id=cls.version.id).annotate(
            relative_credits=Value(gey.relative_credits, output_field=IntegerField())
        ).first()
        cls.user = UserFactory()
        cls.offer = EducationGroupYear.objects.filter(id=cls.training.id).annotate(
            relative_credits=Value(gey.relative_credits, output_field=IntegerField())
        ).first()
        url_kwargs = {
            'acronym': cls.learning_unit_year.acronym,
            'year': cls.learning_unit_year.academic_year.year
        }
        cls.url = reverse(LEARNING_UNIT_API_HEAD + EducationGroupRootsList.name, kwargs=url_kwargs)

    def setUp(self):
        self.client.force_authenticate(user=self.user)

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
        invalid_url = reverse(
            LEARNING_UNIT_API_HEAD + EducationGroupRootsList.name,
            kwargs={'acronym': 'ACRO', 'year': 2019}
        )
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_results(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = EducationGroupRootsListSerializer(
            [self.annotated_version],
            many=True,
            context={
                'request': RequestFactory().get(self.url),
                'language': settings.LANGUAGE_CODE_FR,
                'learning_unit_year': self.learning_unit_year
            }
        )
        self.assertEqual(response.data, serializer.data)


class LearningUnitPrerequisitesViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)

        cls.education_group_year = TrainingFactory(
            acronym='DROI1BA',
            partial_acronym='LDROI1000',
            academic_year=cls.academic_year
        )
        cls.version = StandardEducationGroupVersionFactory(offer=cls.education_group_year)
        cls.learning_unit_year = LearningUnitYearFactory(
            academic_year=cls.academic_year,
            learning_container_year__academic_year=cls.academic_year
        )
        cls.prerequisite = PrerequisiteFactory(
            learning_unit_year=cls.learning_unit_year,
            education_group_year=cls.education_group_year
        )
        PrerequisiteItemFactory(prerequisite=cls.prerequisite)
        cls.user = UserFactory()
        url_kwargs = {
            'acronym': cls.learning_unit_year.acronym,
            'year': cls.learning_unit_year.academic_year.year
        }
        cls.url = reverse(LEARNING_UNIT_API_HEAD + LearningUnitPrerequisitesList.name, kwargs=url_kwargs)

    def setUp(self):
        self.client.force_authenticate(user=self.user)

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
        invalid_url = reverse(
            LEARNING_UNIT_API_HEAD + LearningUnitPrerequisitesList.name,
            kwargs={'acronym': 'ACRO', 'year': 2019}
        )
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_results(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = LearningUnitYearPrerequisitesListSerializer(
            [self.prerequisite],
            many=True,
            context={
                'request': RequestFactory().get(self.url),
                "test": 'test',
                'language': settings.LANGUAGE_CODE_FR
            }
        )
        self.assertListEqual(response.data, serializer.data)
