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
from django.test import TestCase

from base.utils.urls import reverse_with_get
from education_group.ddd.factories.group import GroupFactory
from education_group.tests.ddd.factories.training import TrainingFactory
from education_group.tests.factories.auth.central_manager import CentralManagerFactory
from reference.tests.factories.language import FrenchLanguageFactory


class TestTrainingUpdateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        FrenchLanguageFactory()
        cls.central_manager = CentralManagerFactory()
        cls.url = reverse_with_get(
            "training_update",
            kwargs={"code": "CODE", "year": 2020, "title": "ACRONYM"},
            get={"path_to": "1|2|3"}
        )

    def setUp(self):
        self.client.force_login(self.central_manager.person.user)

    @mock.patch("education_group.ddd.service.read.get_training_service.get_training")
    @mock.patch("education_group.ddd.service.read.get_group_service.get_group")
    def test_should_display_forms_when_good_get_request(self, mock_get_group, mock_get_training):
        mock_get_training.return_value = TrainingFactory()
        mock_get_group.return_value = GroupFactory()

        response = self.client.get(self.url)

        context = response.context
        self.assertTrue(context["training_form"])
        self.assertTrue(context["content_formset"])
        self.assertTemplateUsed(response, "education_group_app/training/upsert/update.html")
