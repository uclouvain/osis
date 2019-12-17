from typing import Dict, List

from rest_framework.test import APITestCase


class APIFilterTestCaseData:
    filters: Dict[str] = None
    expected_result = None

    def __init__(self, filters, expected_result):
        self.filters = filters
        self.expected_result = expected_result


class APITestCasesMixin(APITestCase):

    url = None
    methods_not_allowed = None
    api_with_pagination = True
    api_with_filters = True

    def __init__(self, *args, **kwargs):
        super(APITestCasesMixin, self).__init__(*args, **kwargs)
        if not self.url:
            raise NotImplementedError("Param {} must be set".format('url'))

    def test_get_not_authorized(self):
        pass

    def test_methods_not_allowed(self):
        pass

    def test_pagination(self):
        if not self.api_with_pagination:
            return
        pass

    def get_filter_test_cases(self) -> List[APIFilterTestCaseData]:
        raise NotImplementedError()

    def test_filters(self):
        for filters, expected_result in self.get_filter_test_cases():
            response = self.client.get(self.url, data=filters)



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
            'language': settings.LANGUAGE_CODE_EN
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
                        'language': settings.LANGUAGE_CODE_EN
                    },
                )
                self.assertEqual(response.data['results'], serializer.data)
