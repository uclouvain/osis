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
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.education_group_type import MiniTrainingEducationGroupTypeFactory
from education_group.tests.factories.auth.central_manager import CentralManagerFactory


class TestCreate(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.mini_training_type = MiniTrainingEducationGroupTypeFactory()

        cls.central_manager = CentralManagerFactory()
        cls.url = reverse("mini_training_create", args=[cls.mini_training_type.name])

    def setUp(self) -> None:
        self.client.force_login(self.central_manager.person.user)

    def test_url_is_accessible(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "education_group_app/mini_training/upsert/create.html")
