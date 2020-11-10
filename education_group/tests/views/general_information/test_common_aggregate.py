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
import urllib

from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotFound
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.admission_condition import AdmissionConditionFactory
from base.tests.factories.education_group_year import EducationGroupYearCommonAgregationFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from base.tests.factories.user import UserFactory
from education_group.tests.factories.auth.central_manager import CentralManagerFactory
from education_group.views.general_information.common_aggregate import Tab


class TestCommonAggregateAdmissionCondition(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonWithPermissionsFactory('view_educationgroup')
        cls.common_aggregate_education_group_year = EducationGroupYearCommonAgregationFactory(academic_year__year=2018)
        AdmissionConditionFactory(education_group_year=cls.common_aggregate_education_group_year)
        cls.url = reverse('common_aggregate_admission_condition', kwargs={'year': 2018})

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
        dummy_url = reverse('common_aggregate_admission_condition', kwargs={'year': 1990})
        response = self.client.get(dummy_url)

        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)

    def test_case_common_exist_but_admission_condition_not_exist(self):
        EducationGroupYearCommonAgregationFactory(academic_year__year=1990)

        dummy_url = reverse('common_aggregate_admission_condition', kwargs={'year': 1990})
        response = self.client.get(dummy_url)

        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "education_group_app/general_information/common_aggregate.html")

    def test_assert_context_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context['object'], self.common_aggregate_education_group_year)
        expected_publish_url = reverse('publish_common_aggregate_admission_condition', kwargs={
            'year': self.common_aggregate_education_group_year.academic_year.year
        })
        self.assertEqual(response.context['publish_url'], expected_publish_url)
        self.assertEqual(
            response.context['admission_condition'],
            self.common_aggregate_education_group_year.admissioncondition
        )
        self.assertIn("tab_urls", response.context)
        self.assertIn("can_edit_information", response.context)

    def test_assert_active_tabs_is_content_and_others_are_not_active(self):
        response = self.client.get(self.url)

        self.assertEqual(len(response.context['tab_urls']), 1)
        self.assertTrue(response.context['tab_urls'][Tab.ADMISSION_CONDITION]['active'])


class TestUpdateGetCommonAggregateAdmissionCondition(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.common_education_group_year = EducationGroupYearCommonAgregationFactory(academic_year__year=2018)
        AdmissionConditionFactory(education_group_year=cls.common_education_group_year)

        cls.section_name = "alert_message"
        cls.section_title = "Message d'alerte"
        cls.central_manager = CentralManagerFactory(entity=cls.common_education_group_year.management_entity)

        params = {'section': cls.section_name, 'title': cls.section_title}
        cls.url = reverse('update_common_aggregate_admission_condition', kwargs={'year': 2018}) + \
            "?" + (urllib.parse.urlencode(params))

    def setUp(self) -> None:
        self.client.force_login(self.central_manager.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(urllib.parse.quote(self.url)))

    def test_case_user_have_not_permission(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_case_aggregate_common_not_exists(self):
        dummy_url = reverse('update_common_aggregate_admission_condition', kwargs={'year': 1990})
        response = self.client.get(dummy_url)

        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "education_group/condition_text_edit.html")

    def test_assert_context(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response.context['title'], self.section_title)


class TestUpdatePostCommonAggregateAdmissionCondition(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.common_education_group_year = EducationGroupYearCommonAgregationFactory(academic_year__year=2018)
        AdmissionConditionFactory(education_group_year=cls.common_education_group_year)

        cls.section_name = "alert_message"
        cls.section_title = "Message d'alerte"
        cls.central_manager = CentralManagerFactory(entity=cls.common_education_group_year.management_entity)

        params = {'section': cls.section_name, 'title': cls.section_title}
        cls.url = reverse('update_common_aggregate_admission_condition', kwargs={'year': 2018}) + \
            "?" + (urllib.parse.urlencode(params))

    def setUp(self) -> None:
        self.client.force_login(self.central_manager.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(urllib.parse.quote(self.url)))

    def test_case_user_have_not_permission(self):
        self.client.force_login(UserFactory())
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_case_assert_redirection(self):
        response = self.client.post(self.url, data={
            'section': self.section_name,
            'text_fr': 'Text in french',
            'text_en': 'Text in english',
        })

        expected_redirection = reverse(
            'common_aggregate_admission_condition',
            kwargs={'year': self.common_education_group_year.academic_year.year}
        )
        self.assertRedirects(response, expected_redirection, fetch_redirect_response=False)
