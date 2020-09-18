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

from django.conf import settings
from django.db.models import F
from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.test import APITestCase

from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.campus import CampusFactory
from base.tests.factories.education_group_year import TrainingFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory
from education_group.api.serializers.education_group_title import EducationGroupTitleSerializer
from education_group.api.serializers.training import TrainingListSerializer, TrainingDetailSerializer
from reference.tests.factories.domain import DomainFactory


class TrainingTitleTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        anac = AcademicYearFactory()
        cls.egy = TrainingFactory(academic_year=anac)
        cls.person = PersonFactory()
        cls.url = reverse('education_group_api_v1:trainingstitle_read', kwargs={
            'acronym': cls.egy.acronym,
            'year': cls.egy.academic_year.year
        })

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

    def test_get_results_case_education_group_year_not_found(self):
        invalid_url = reverse('education_group_api_v1:trainingstitle_read', kwargs={
            'acronym': 'ACRO',
            'year': 2019
        })
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_results(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = EducationGroupTitleSerializer(self.egy, context={'language': settings.LANGUAGE_CODE})
        self.assertEqual(response.data, serializer.data)


class GetAllTrainingTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse('education_group_api_v1:training-list')

        cls.academic_year = AcademicYearFactory(year=2018)
        TrainingFactory(acronym='BIR1BA', partial_acronym='LBIR1000I', academic_year=cls.academic_year)
        TrainingFactory(acronym='AGRO1BA', partial_acronym='LAGRO2111C', academic_year=cls.academic_year)
        TrainingFactory(acronym='MED12M', partial_acronym='LMED12MA', academic_year=cls.academic_year)

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete', 'put']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_all_training_ensure_response_have_next_previous_results_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue('previous' in response.data)
        self.assertTrue('next' in response.data)
        self.assertTrue('results' in response.data)

        self.assertTrue('count' in response.data)
        expected_count = EducationGroupYear.objects.filter(
            education_group_type__category=education_group_categories.TRAINING,
        ).count()
        self.assertEqual(response.data['count'], expected_count)

    def test_get_all_training_ensure_default_order(self):
        """ This test ensure that default order is academic_year [DESC Order] + acronym [ASC Order]"""
        TrainingFactory(acronym='BIR1BA', partial_acronym='LBIR1000I', academic_year__year=2017)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        trainings = EducationGroupYear.objects.filter(
            education_group_type__category=education_group_categories.TRAINING,
        ).order_by('-academic_year__year', 'acronym')
        serializer = TrainingListSerializer(trainings, many=True, context={
            'request': RequestFactory().get(self.url),
            'language': settings.LANGUAGE_CODE_FR
        })
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_all_training_specify_ordering_field(self):
        ordering_managed = ['acronym', 'partial_acronym', 'title', 'title_english']

        for order in ordering_managed:
            with self.subTest(ordering=order):
                query_string = {api_settings.ORDERING_PARAM: order}
                response = self.client.get(self.url, data=query_string)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                trainings = EducationGroupYear.objects.filter(
                    education_group_type__category=education_group_categories.TRAINING,
                ).order_by(order)
                serializer = TrainingListSerializer(
                    trainings,
                    many=True,
                    context={
                        'request': RequestFactory().get(self.url, query_string),
                        'language': settings.LANGUAGE_CODE_FR
                    },
                )
                self.assertEqual(response.data['results'], serializer.data)


class FilterTrainingTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse('education_group_api_v1:training-list')
        cls.trainings = []
        campus = CampusFactory(name='CAMPUS BENJ')
        for year in [2018, 2019, 2020]:
            academic_year = AcademicYearFactory(year=year)
            cls.trainings.append(
                TrainingFactory(acronym='BIR1BA', partial_acronym='LBIR1000I', academic_year=academic_year)
            )
            cls.trainings.append(
                TrainingFactory(acronym='AGRO1BA', partial_acronym='LAGRO2111C', academic_year=academic_year)
            )
            cls.trainings.append(
                TrainingFactory(
                    acronym='MED12M', partial_acronym='LMED12MA', academic_year=academic_year,
                    main_teaching_campus=campus
                )
            )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_training_case_filter_from_year_params(self):
        query_string = {'from_year': 2020}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        trainings = EducationGroupYear.objects.filter(
            education_group_type__category=education_group_categories.TRAINING,
            academic_year__year__gte=query_string['from_year']
        ).order_by('-academic_year__year', 'acronym')

        serializer = TrainingListSerializer(
            trainings,
            many=True,
            context={
                'request': RequestFactory().get(self.url, query_string),
                'language': settings.LANGUAGE_CODE_EN
            },
        )
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_training_case_filter_to_year_params(self):
        query_string = {'to_year': 2019}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        trainings = EducationGroupYear.objects.filter(
            education_group_type__category=education_group_categories.TRAINING,
            academic_year__year__lte=query_string['to_year']
        ).order_by('-academic_year__year', 'acronym')

        serializer = TrainingListSerializer(
            trainings,
            many=True,
            context={
                'request': RequestFactory().get(self.url, query_string),
                'language': settings.LANGUAGE_CODE_FR
            },
        )
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_training_case_filter_type_params(self):
        query_string = {'in_type': 'continue'}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        trainings = EducationGroupYear.objects.filter(
            education_group_type__category=education_group_categories.TRAINING,
            education_group_type__name__contains=query_string['in_type']
        )

        serializer = TrainingListSerializer(
            trainings,
            many=True,
            context={'request': RequestFactory().get(self.url, query_string)},
        )
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_training_case_filter_campus(self):
        query_string = {'campus': self.trainings[2].main_teaching_campus.name}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = TrainingListSerializer(
            [self.trainings[2], self.trainings[5], self.trainings[8]],
            many=True,
            context={'request': RequestFactory().get(self.url, query_string)},
        )
        self.assertCountEqual(response.data['results'], serializer.data)

    def test_get_filter_by_multiple_education_group_type(self):
        """
        This test ensure that multiple filtering by education_group_type will act as an OR
        """
        data = {'education_group_type': [training.education_group_type.name for training in self.trainings]}

        response = self.client.get(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 9)


class GetTrainingTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        domain = DomainFactory()
        cls.training = TrainingFactory(
            acronym='BIR1BA',
            partial_acronym='LBIR1000I',
            academic_year=cls.academic_year,
            main_domain=domain
        )
        cls.user = UserFactory()
        cls.url = reverse('education_group_api_v1:training_read', kwargs={
            'acronym': cls.training.acronym,
            'year': cls.academic_year.year
        })

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

    def test_get_valid_training(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        annotated_training = EducationGroupYear.objects.annotate(
            domain_code=F('main_domain__code'),
            domain_name=F('main_domain__name'),
        ).get(id=self.training.id)
        serializer = TrainingDetailSerializer(
            annotated_training,
            context={
                'request': RequestFactory().get(self.url),
                'language': settings.LANGUAGE_CODE_FR
            },
        )
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_training_case_not_found(self):
        invalid_url = reverse('education_group_api_v1:training_read', kwargs={
            'acronym': 'ACRO',
            'year': 2033
        })
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_none_if_no_domain(self):
        training = TrainingFactory(
            academic_year=self.academic_year,
            main_domain=None
        )
        url = reverse('education_group_api_v1:training_read', kwargs={
            'acronym': training.acronym,
            'year': self.academic_year.year
        })
        response = self.client.get(url)
        self.assertIsNone(response.data['domain_name'])
        self.assertIsNone(response.data['domain_code'])

    def test_get_parent_domain_name_if_has_parent(self):
        domain = DomainFactory(parent=DomainFactory())
        training = TrainingFactory(
            academic_year=self.academic_year,
            main_domain=domain
        )
        url = reverse('education_group_api_v1:training_read', kwargs={
            'acronym': training.acronym,
            'year': self.academic_year.year
        })
        response = self.client.get(url)
        self.assertEqual(response.data['domain_name'], domain.parent.name)
        self.assertEqual(response.data['domain_code'], domain.code)
