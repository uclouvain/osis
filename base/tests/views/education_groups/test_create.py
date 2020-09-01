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
from datetime import datetime
from unittest import mock

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, HttpResponse
from django.test import TestCase
from django.urls import reverse
from waffle.testutils import override_flag

from base.forms.education_group.group import GroupYearModelForm
from base.forms.education_group.mini_training import MiniTrainingYearModelForm
from base.forms.education_group.training import TrainingEducationGroupYearForm
from base.models.enums import education_group_categories, organization_type, internship_presence
from base.models.enums.active_status import ACTIVE
from base.models.enums.education_group_categories import TRAINING
from base.models.enums.entity_type import FACULTY
from base.models.enums.schedule_type import DAILY
from base.models.exceptions import ValidationWarning
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.authorized_relationship import AuthorizedRelationshipFactory
from base.tests.factories.business.learning_units import GenerateAcademicYear
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.person import PersonFactory
from base.views.education_groups.create import PERMS_BY_CATEGORY
from education_group.tests.factories.auth.central_manager import CentralManagerFactory
from reference.tests.factories.language import LanguageFactory


class TestCreateMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_academic_year = AcademicYearFactory(current=True)
        start_year = AcademicYearFactory(year=cls.current_academic_year.year + 1)
        end_year = AcademicYearFactory(year=cls.current_academic_year.year + 10)
        cls.generated_ac_years = GenerateAcademicYear(start_year, end_year)
        cls.parent_education_group_year = EducationGroupYearFactory(academic_year=cls.current_academic_year)

        cls.test_categories = [
            education_group_categories.GROUP,
            education_group_categories.TRAINING,
            education_group_categories.MINI_TRAINING,
        ]

        cls.education_group_types = [
            EducationGroupTypeFactory(category=category)
            for category in cls.test_categories
        ]
        cls.organization = OrganizationFactory(type=organization_type.MAIN)
        cls.entity = EntityFactory(organization=cls.organization)
        cls.entity_version = EntityVersionFactory(entity=cls.entity, entity_type=FACULTY, start_date=datetime.now())
        cls.language = LanguageFactory()
        cls.person = PersonFactory()
        CentralManagerFactory(person=cls.person, entity=cls.entity)


class TestValidateField(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory()
        cls.person = PersonFactory()
        cls.url = reverse('validate_education_group_field', args=[TRAINING])

    def setUp(self):
        self.client.force_login(self.person.user)

        mock_clean_acronym = mock.patch(
            "base.models.education_group_year.EducationGroupYear.clean_acronym",
            return_value=None
        )
        self.mocked_clean_acronym = mock_clean_acronym.start()
        self.addCleanup(mock_clean_acronym.stop)

        mock_clean_partial_acronym = mock.patch(
            "base.models.education_group_year.EducationGroupYear.clean_partial_acronym",
            return_value=None
        )
        self.mocked_clean_partial_acronym = mock_clean_partial_acronym.start()
        self.addCleanup(mock_clean_partial_acronym.stop)

    def test_response_should_be_empty_when_fields_are_valid(self):
        response = self.client.get(
            self.url,
            data={"academic_year": self.academic_year.pk, "acronym": "TEST"},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {}
        )

    def test_response_should_contain_error_message_when_field_not_valid(self):
        self.mocked_clean_acronym.side_effect = ValidationError({"acronym": "error acronym"})
        self.mocked_clean_partial_acronym.side_effect = ValidationWarning({"partial_acronym": "error partial"})

        response = self.client.get(
            self.url,
            data={"academic_year": self.academic_year.pk, "acronym": "TEST"},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"acronym": {"msg": "error acronym", "level": messages.DEFAULT_TAGS[messages.ERROR]},
             "partial_acronym": {"msg": "error partial", "level": messages.DEFAULT_TAGS[messages.WARNING]}}
        )
