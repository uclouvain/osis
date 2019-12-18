from typing import Dict, List

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.models.enums import learning_unit_enrollment_state
from base.models.learning_unit_enrollment import LearningUnitEnrollment
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.user import UserFactory
from learning_unit_enrollment.api.serializers.learning_unit_enrollment import LearningUnitEnrollmentSerializer


class FilterEnrollmentsByStudentTestCase(APITestCase):

    def setUp(self):
        self.offer_acronym = 'DROI1BA'
        self.registration_id = '00000001'
        self.url = reverse(
            'learning_unit_enrollment_api_v1:enrollment-list-by-student',
            kwargs={'registration_id': self.registration_id}
        )

        self.user = UserFactory()

        for year in [2018, 2019, 2020]:
            LearningUnitEnrollmentFactory(
                offer_enrollment__student__person__user=self.user,
                offer_enrollment__student__registration_id=self.registration_id,
                offer_enrollment__education_group_year__academic_year__year=year,
                offer_enrollment__education_group_year__acronym=self.offer_acronym,
                learning_unit_year__academic_year__year=year,
            )
        self.client.force_authenticate(user=self.user)

    def test_get_training_case_filter_year_params(self):
        query_string = {'year': 2018}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = LearningUnitEnrollmentSerializer(
            LearningUnitEnrollment.objects.filter(learning_unit_year__academic_year__year=2018),
            many=True,
        )
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_training_case_filter_offer_acronym_params(self):
        query_string = {'offer_acronym': self.offer_acronym}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = LearningUnitEnrollmentSerializer(
            LearningUnitEnrollment.objects.filter(offer_enrollment__education_group_year__acronym=self.offer_acronym),
            many=True,
        )
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_training_case_filter_enrollment_state_params(self):
        query_string = {'enrollment_state': learning_unit_enrollment_state.ENROLLED}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = LearningUnitEnrollmentSerializer(
            LearningUnitEnrollment.objects.filter(enrollment_state=learning_unit_enrollment_state.ENROLLED),
            many=True,
        )
        self.assertEqual(response.data['results'], serializer.data)

    # FIXME :: use mixin instead of copy-pasted code
    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_pagination(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue('previous' in response.data)
        self.assertTrue('next' in response.data)
        self.assertTrue('results' in response.data)
        self.assertTrue('count' in response.data)


class LearningUnitEnrollmentSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.year = 2020
        cls.learning_unit_acronym = 'LDROI1001'
        cls.url = reverse(
            'learning_unit_enrollment_api_v1:enrollment-list-by-learning-unit',
            kwargs={'year': cls.year, 'acronym': cls.learning_unit_acronym}
        )
        cls.learning_unit_enrollment = LearningUnitEnrollmentFactory(
            offer_enrollment__education_group_year__academic_year__year=cls.year,
            learning_unit_year__academic_year__year=cls.year,
            learning_unit_year__acronym=cls.learning_unit_acronym,
        )
        cls.serializer = LearningUnitEnrollmentSerializer(cls.learning_unit_enrollment)

    def test_contains_expected_fields(self):
        expected_fields = [
            'registration_id',
            'student_first_name',
            'student_last_name',
            'student_email',
            'learning_unit_acronym',
            'education_group_acronym',
            'academic_year',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_academic_year_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['academic_year'],
            self.year
        )

    def test_ensure_education_group_type_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['learning_unit_acronym'],
            self.learning_unit_acronym
        )
