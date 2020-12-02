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
from django.db.models import F
from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.test import APITestCase

from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import TrainingFactory
from base.tests.factories.hops import HopsFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory
from education_group.api.serializers.education_group_title import EducationGroupTitleSerializer
from education_group.api.serializers.training import TrainingListSerializer, TrainingDetailSerializer
from education_group.tests.factories.group_year import GroupYearFactory
from program_management.models.education_group_version import EducationGroupVersion
from program_management.tests.factories.education_group_version import StandardEducationGroupVersionFactory, \
    StandardTransitionEducationGroupVersionFactory
from reference.tests.factories.domain import DomainFactory


class TrainingTitleTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        anac = AcademicYearFactory()
        cls.egy = TrainingFactory(academic_year=anac)
        cls.version = StandardEducationGroupVersionFactory(offer=cls.egy)
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

        serializer = EducationGroupTitleSerializer(self.version, context={'language': settings.LANGUAGE_CODE})
        self.assertEqual(response.data, serializer.data)


class GetAllTrainingTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse('education_group_api_v1:training-list')

        cls.academic_year = AcademicYearFactory(year=2018)
        offer1 = TrainingFactory(acronym='BIR1BA', partial_acronym='LBIR1000I', academic_year=cls.academic_year)
        offer2 = TrainingFactory(acronym='AGRO1BA', partial_acronym='LAGRO2111C', academic_year=cls.academic_year)
        offer3 = TrainingFactory(acronym='MED12M', partial_acronym='LMED12MA', academic_year=cls.academic_year)
        StandardEducationGroupVersionFactory(offer=offer1)
        StandardEducationGroupVersionFactory(offer=offer2)
        StandardEducationGroupVersionFactory(offer=offer3)

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

        versions = EducationGroupVersion.objects.filter(
            offer__education_group_type__category=education_group_categories.TRAINING,
        ).order_by('-offer__academic_year__year', 'offer__acronym')
        serializer = TrainingListSerializer(versions, many=True, context={
            'request': RequestFactory().get(self.url),
            'language': settings.LANGUAGE_CODE_FR
        })
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_all_training_specify_ordering_field(self):
        ordering_managed = ['offer__acronym', 'root_group__partial_acronym', 'offer__title', 'offer__title_english']

        for order in ordering_managed:
            with self.subTest(ordering=order):
                query_string = {api_settings.ORDERING_PARAM: order}
                response = self.client.get(self.url, data=query_string)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                versions = EducationGroupVersion.objects.filter(
                    offer__education_group_type__category=education_group_categories.TRAINING,
                ).order_by(order)
                serializer = TrainingListSerializer(
                    versions,
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
        cls.offers_by_year = {}
        cls.standards_by_year = {}
        for year in [2018, 2019, 2020]:
            academic_year = AcademicYearFactory(year=year)
            offer1 = TrainingFactory(acronym='BIR1BA', partial_acronym='LBIR1000I', academic_year=academic_year)
            offer2 = TrainingFactory(acronym='AGRO1BA', partial_acronym='LAGRO2111C', academic_year=academic_year)
            offer3 = TrainingFactory(acronym='MED12M', partial_acronym='LMED12MA', academic_year=academic_year)
            group1 = GroupYearFactory(partial_acronym=offer1.partial_acronym, academic_year=offer1.academic_year)
            group2 = GroupYearFactory(partial_acronym=offer2.partial_acronym, academic_year=offer2.academic_year)
            group3 = GroupYearFactory(partial_acronym=offer3.partial_acronym, academic_year=offer3.academic_year)
            standard1 = StandardEducationGroupVersionFactory(offer=offer1, root_group=group1)
            standard2 = StandardEducationGroupVersionFactory(offer=offer2, root_group=group2)
            standard3 = StandardEducationGroupVersionFactory(offer=offer3, root_group=group3)
            cls.offers_by_year[year] = [offer1, offer2, offer3]
            cls.standards_by_year[year] = [standard1, standard2, standard3]
        StandardTransitionEducationGroupVersionFactory()

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_training_case_version_type_param_is_not_allowed(self):
        query_string = {'version_type': 'test'}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_training_case_version_type_param_is_transition(self):
        query_string = {'version_type': 'transition'}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        trainings = EducationGroupVersion.objects.filter(is_transition=True)

        serializer = TrainingListSerializer(
            trainings,
            many=True,
            context={'request': RequestFactory().get(self.url, query_string)},
        )
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_training_case_version_type_param_is_special(self):
        query_string = {'version_type': 'special'}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        trainings = EducationGroupVersion.objects.exclude(version_name__iexact='')

        serializer = TrainingListSerializer(
            trainings,
            many=True,
            context={'request': RequestFactory().get(self.url, query_string)},
        )
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_training_case_filter_from_year_params(self):
        query_string = {'from_year': 2020}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        versions = EducationGroupVersion.objects.filter(
            offer__education_group_type__category=education_group_categories.TRAINING,
            offer__academic_year__year__gte=query_string['from_year'],
            is_transition=False
        ).order_by('-offer__academic_year__year', 'offer__acronym')

        serializer = TrainingListSerializer(
            versions,
            many=True,
            context={
                'request': RequestFactory().get(self.url, query_string),
                'language': settings.LANGUAGE_CODE_FR
            },
        )
        self.assertCountEqual(response.data['results'], serializer.data)

    def test_get_training_case_filter_to_year_params(self):
        query_string = {'to_year': 2019}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        versions = EducationGroupVersion.standard.filter(
            offer__education_group_type__category=education_group_categories.TRAINING,
            offer__academic_year__year__lte=query_string['to_year'],
            is_transition=False
        ).order_by('-offer__academic_year__year', 'offer__acronym')

        serializer = TrainingListSerializer(
            versions,
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
        query_string = {'campus': self.standards_by_year[2018][2].root_group.main_teaching_campus.name}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = TrainingListSerializer(
            [self.standards_by_year[2018][2]],
            many=True,
            context={'request': RequestFactory().get(self.url, query_string)},
        )
        self.assertCountEqual(response.data['results'], serializer.data)

    def test_get_filter_by_multiple_education_group_type(self):
        """
        This test ensure that multiple filtering by education_group_type will act as an OR
        """
        data = {'education_group_type': [training.education_group_type.name for training in self.offers_by_year[2018]]}

        response = self.client.get(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_get_training_case_filter_lowercase_acronym(self):
        query_string = {'acronym': 'agro1ba'}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        versions = EducationGroupVersion.objects.filter(
            offer__education_group_type__category=education_group_categories.TRAINING,
            offer__acronym__icontains='agro1ba'
        ).order_by('-offer__academic_year__year', 'offer__acronym')

        serializer = TrainingListSerializer(
            versions,
            many=True,
            context={
                'request': RequestFactory().get(self.url, query_string),
                'language': settings.LANGUAGE_CODE_FR
            },
        )
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_training_case_filter_ares_ability(self):
        hops = HopsFactory()
        TrainingFactory(hops=hops)
        query_string = {'ares_ability': hops.ares_ability}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        versions = EducationGroupVersion.objects.filter(
            offer__hops__ares_ability=hops.ares_ability
        ).order_by('-offer__academic_year__year', 'offer__acronym')

        serializer = TrainingListSerializer(
            versions,
            many=True,
            context={
                'request': RequestFactory().get(self.url, query_string),
                'language': settings.LANGUAGE_CODE_FR
            },
        )
        self.assertEqual(response.data['results'], serializer.data)


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
        cls.version = StandardEducationGroupVersionFactory(offer=cls.training)
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
        annotated_version = EducationGroupVersion.objects.annotate(
            domain_code=F('offer__main_domain__code'),
            domain_name=F('offer__main_domain__name'),
        ).get(id=self.version.id)
        serializer = TrainingDetailSerializer(
            annotated_version,
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
            main_domain=None,
        )
        StandardEducationGroupVersionFactory(offer=training)
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
        StandardEducationGroupVersionFactory(offer=training)
        url = reverse('education_group_api_v1:training_read', kwargs={
            'acronym': training.acronym,
            'year': self.academic_year.year
        })
        response = self.client.get(url)
        self.assertEqual(response.data['domain_name'], domain.parent.name)
        self.assertEqual(response.data['domain_code'], domain.code)
