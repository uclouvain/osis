from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotFound
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.admission_condition import AdmissionConditionFactory
from base.tests.factories.education_group_year import EducationGroupYearCommonBachelorFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from base.tests.factories.user import UserFactory
from education_group.views.general_information.common_bachelor import Tab


class TestCommonBachelorAdmissionCondition(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonWithPermissionsFactory('view_educationgroup')
        cls.common_bachelor_education_group_year = EducationGroupYearCommonBachelorFactory(academic_year__year=2018)
        AdmissionConditionFactory(education_group_year=cls.common_bachelor_education_group_year)
        cls.url = reverse('common_bachelor_admission_condition', kwargs={'year': 2018})

    def setUp(self) -> None:
        self.client.force_login(self.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_case_user_have_not_permission(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_case_common_and_admission_condition_not_exists(self):
        dummy_url = reverse('common_bachelor_admission_condition', kwargs={'year': 1990})
        response = self.client.get(dummy_url)

        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)

    def test_case_common_exist_but_admission_condition_not_exist(self):
        EducationGroupYearCommonBachelorFactory(academic_year__year=1990)

        dummy_url = reverse('common_bachelor_admission_condition', kwargs={'year': 1990})
        response = self.client.get(dummy_url)

        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "general_information/common_bachelor.html")

    def test_assert_context_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context['object'], self.common_bachelor_education_group_year)
        self.assertEqual(
            response.context['admission_condition'],
            self.common_bachelor_education_group_year.admissioncondition
        )
        self.assertIn("tab_urls", response.context)
        self.assertIn("can_edit_information", response.context)

    def test_assert_active_tabs_is_content_and_others_are_not_active(self):
        response = self.client.get(self.url)

        self.assertEqual(len(response.context['tab_urls']), 1)
        self.assertTrue(response.context['tab_urls'][Tab.ADMISSION_CONDITION]['active'])
