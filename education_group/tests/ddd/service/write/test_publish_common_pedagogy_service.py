# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.test import TestCase, override_settings

from education_group.ddd.command import PublishCommonPedagogyCommand
from education_group.ddd.service.write import publish_common_pedagogy_service


@override_settings(
    ESB_API_URL="api.esb.com",
    ESB_AUTHORIZATION="Basic dummy:1234",
    ESB_REFRESH_COMMON_PEDAGOGY_ENDPOINT="common/{year}/refresh",
    REQUESTS_TIMEOUT=20
)
class TestPublishCommonPedagogyService(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cmd = PublishCommonPedagogyCommand(year=2018)

    def setUp(self):
        self.requests_get_patcher = mock.patch('requests.get', return_value=HttpResponse)
        self.mocked_requests_get = self.requests_get_patcher.start()
        self.addCleanup(self.requests_get_patcher.stop)

    @override_settings(ESB_REFRESH_COMMON_PEDAGOGY_ENDPOINT=None)
    def test_publish_case_missing_settings(self):
        with self.assertRaises(ImproperlyConfigured):
            publish_common_pedagogy_service.publish_common_pedagogy(self.cmd)

    def test_publish_call_external_service(self):
        publish_common_pedagogy_service.publish_common_pedagogy(self.cmd)

        expected_publish_url = "api.esb.com/common/{year}/refresh".format(year=self.cmd.year)
        self.mocked_requests_get.assert_called_with(
            expected_publish_url,
            headers={"Authorization": "Basic dummy:1234"},
            timeout=20
        )

