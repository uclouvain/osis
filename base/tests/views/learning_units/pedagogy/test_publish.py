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
import mock
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.test import TestCase, override_settings
from django.urls import reverse

from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory


@override_settings(
    ESB_API_URL="api.esb.com",
    ESB_REFRESH_LEARNING_UNIT_PEDAGOGY_ENDPOINT="learningUnits/{year}/{code}/resetCache",
    LEARNING_UNIT_PORTAL_URL="https://dummy-site.be/cours-{year}-{code}"
)
class TestPublishLearningPedagogy(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()
        cls.learning_unit_year = LearningUnitYearFactory(acronym="LOSIS1452", academic_year__year=2020)

        cls.url = reverse(
            "publish_and_access_learning_unit_pedagogy",
            kwargs={"code": cls.learning_unit_year.acronym, "year": cls.learning_unit_year.academic_year.year}
        )

    def setUp(self) -> None:
        self.client.force_login(self.person.user)

    @mock.patch('requests.get', return_value=HttpResponse)
    def test_should_redirect_to_learning_unit_portal_when_refresh_succeed(self, mock_request_get):
        response = self.client.get(self.url, follow=False)

        expected_url = settings.LEARNING_UNIT_PORTAL_URL.format(
            code=self.learning_unit_year.acronym,
            year=self.learning_unit_year.academic_year.year
        )
        self.assertRedirects(response, expected_url, fetch_redirect_response=False)

    @mock.patch('requests.get', return_value=HttpResponseNotFound)
    def test_should_redirect_to_learning_unit_pedagogy_when_refresh_failed(self, mock_request_get):
        response = self.client.get(self.url, follow=False)

        expected_url = reverse(
            'view_educational_information',
            kwargs={'learning_unit_year_id': self.learning_unit_year.pk}
        )
        self.assertRedirects(response, expected_url, fetch_redirect_response=False)
