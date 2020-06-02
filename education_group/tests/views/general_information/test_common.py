from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotFound
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.education_group_year import EducationGroupYearCommonFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from base.tests.factories.user import UserFactory
from education_group.views.general_information.common import Tab


class TestCommonGeneralInformation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonWithPermissionsFactory('view_educationgroup')
        cls.common_education_group_year = EducationGroupYearCommonFactory(academic_year__year=2018)
        cls.url = reverse('common_general_information', kwargs={'year': 2018})

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

    def test_case_common_not_exists(self):
        dummy_url = reverse('common_general_information', kwargs={'year': 1990})
        response = self.client.get(dummy_url)

        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "general_information/common.html")

    def test_assert_context_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context['object'], self.common_education_group_year)
        expected_update_url = reverse('education_group_pedagogy_edit', args=[
            self.common_education_group_year.pk,
            self.common_education_group_year.pk
        ])
        self.assertEqual(response.context['update_label_url'], expected_update_url)

        self.assertIn("tab_urls", response.context)
        self.assertIn("sections", response.context)
        self.assertIn("can_edit_information", response.context)

    def test_assert_active_tabs_is_content_and_others_are_not_active(self):
        response = self.client.get(self.url)

        self.assertEqual(len(response.context['tab_urls']), 1)
        self.assertTrue(response.context['tab_urls'][Tab.GENERAL_INFO]['active'])
