from typing import List

from django.test import TestCase, RequestFactory
from django.urls import reverse

from base.models.enums import learning_unit_enrollment_state
from base.models.enums.education_group_categories import Categories
from base.models.learning_unit_enrollment import LearningUnitEnrollment
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.mixin.default_api_tests_cases_mixin import APIDefaultTestsCasesHttpGetMixin, APIFilterTestCaseData
from learning_unit_enrollment.api.serializers.learning_unit_enrollment import LearningUnitEnrollmentSerializer


class EnrollmentsListByStudentTestCase(APIDefaultTestsCasesHttpGetMixin):

    methods_not_allowed = ['post', 'delete', 'put', 'patch']

    @classmethod
    def setUpTestData(cls):
        cls.education_group_acronym = 'DROI1BA'
        cls.registration_id = '00000001'
        cls.url = reverse(
            'learning_unit_enrollment_api_v1:enrollments-list-by-student',
            kwargs={'registration_id': cls.registration_id}
        )

        for year in [2018, 2019, 2020]:
            LearningUnitEnrollmentFactory(
                offer_enrollment__student__person__user=cls.user,
                offer_enrollment__student__registration_id=cls.registration_id,
                offer_enrollment__education_group_year__academic_year__year=year,
                offer_enrollment__education_group_year__acronym=cls.education_group_acronym,
                offer_enrollment__education_group_year__education_group_type__category=Categories.TRAINING,
                learning_unit_year__academic_year__year=year,
            )

    def get_filter_test_cases(self) -> List[APIFilterTestCaseData]:
        return [

            APIFilterTestCaseData(
                filters={'year': 2018},
                expected_result=LearningUnitEnrollmentSerializer(
                    LearningUnitEnrollment.objects.filter(learning_unit_year__academic_year__year=2018),
                    context={'request': RequestFactory().get(self.url)},
                    many=True,
                ).data,
            ),

            APIFilterTestCaseData(
                filters={'education_group_acronym': self.education_group_acronym},
                expected_result=LearningUnitEnrollmentSerializer(
                    LearningUnitEnrollment.objects.filter(
                        offer_enrollment__education_group_year__acronym=self.education_group_acronym
                    ),
                    context={'request': RequestFactory().get(self.url)},
                    many=True,
                ).data,
            ),

            APIFilterTestCaseData(
                filters={'enrollment_state': learning_unit_enrollment_state.ENROLLED},
                expected_result=LearningUnitEnrollmentSerializer(
                    LearningUnitEnrollment.objects.filter(enrollment_state=learning_unit_enrollment_state.ENROLLED),
                    context={'request': RequestFactory().get(self.url)},
                    many=True,
                ).data,
            ),

        ]


class LearningUnitEnrollmentSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.year = 2020
        cls.learning_unit_acronym = 'LDROI1001'
        cls.url = reverse(
            'learning_unit_enrollment_api_v1:enrollments-list-by-learning-unit',
            kwargs={'year': cls.year, 'acronym': cls.learning_unit_acronym}
        )
        cls.learning_unit_enrollment = LearningUnitEnrollmentFactory(
            offer_enrollment__education_group_year__academic_year__year=cls.year,
            learning_unit_year__academic_year__year=cls.year,
            learning_unit_year__acronym=cls.learning_unit_acronym,
        )
        cls.serializer = LearningUnitEnrollmentSerializer(
            cls.learning_unit_enrollment,
            context={'request': RequestFactory().get(cls.url)}
        )

    def test_contains_expected_fields(self):
        expected_fields = [
            'registration_id',
            'student_first_name',
            'student_last_name',
            'student_email',
            'learning_unit_acronym',
            'education_group_acronym',
            'academic_year',
            'education_group_url',
            'learning_unit_url',
            'enrollment_state',
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
