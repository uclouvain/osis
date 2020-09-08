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
import json

from django.test import TestCase
from django.urls import reverse

from base.tests.factories.certificate_aim import CertificateAimFactory
from base.tests.factories.user import SuperUserFactory


class TestCertificateAimAutocomplete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super_user = SuperUserFactory()
        cls.url = reverse("certificate_aim_autocomplete")
        cls.certificate_aim = CertificateAimFactory(
            code=1234,
            section=5,
            description="description",
        )

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url, data={'q': '1234'})
        json_response = str(response.content, encoding='utf8')
        results = json.loads(json_response)['results']
        self.assertEqual(results, [])

    def test_when_param_is_digit_assert_searching_on_code(self):
        # When searching on "code"
        self.client.force_login(user=self.super_user)
        response = self.client.get(self.url, data={'q': '1234'})
        self._assert_result_is_correct(response)

    def test_assert_searching_on_description(self):
        # When searching on "description"
        self.client.force_login(user=self.super_user)
        response = self.client.get(self.url, data={'q': 'descr'})
        self._assert_result_is_correct(response)

    def test_with_filter_by_section(self):
        self.client.force_login(user=self.super_user)
        response = self.client.get(self.url, data={'forward': '{"section": "5"}'})
        self._assert_result_is_correct(response)

    def _assert_result_is_correct(self, response):
        self.assertEqual(response.status_code, 200)
        json_response = str(response.content, encoding='utf8')
        results = json.loads(json_response)['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.certificate_aim.code)
