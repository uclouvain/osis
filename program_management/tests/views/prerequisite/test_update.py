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

import mock
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.test import TestCase
from django.urls import reverse

from base.models.enums import education_group_categories, academic_calendar_type
from base.models.enums.education_group_types import TrainingType
from base.tests.factories.academic_calendar import OpenAcademicCalendarFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory, GroupElementYearChildLeafFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFakerFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_entity import PersonEntityFactory
from education_group.tests.factories.auth.central_manager import CentralManagerFactory
from program_management.ddd.domain.program_tree_version import STANDARD
from program_management.tests.factories.education_group_version import EducationGroupVersionFactory
from program_management.tests.factories.element import ElementGroupYearFactory, ElementLearningUnitYearFactory


class TestUpdateLearningUnitPrerequisite(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2020)
        cls.element_parent = ElementGroupYearFactory(
            group_year__academic_year=cls.academic_year,
            group_year__education_group_type__category=education_group_categories.TRAINING,
            group_year__education_group_type__name=TrainingType.BACHELOR.name
        )
        cls.learning_unit_year_child = LearningUnitYearFakerFactory(
            learning_container_year__academic_year=cls.academic_year
        )
        cls.element_child = ElementLearningUnitYearFactory(
            learning_unit_year=cls.learning_unit_year_child
        )
        EducationGroupVersionFactory(root_group=cls.element_parent.group_year, version_name=STANDARD)

        GroupElementYearFactory(parent_element=cls.element_parent, child_element=cls.element_child)
        cls.person = CentralManagerFactory(entity=cls.element_parent.group_year.management_entity).person
        OpenAcademicCalendarFactory(
            reference=academic_calendar_type.EDUCATION_GROUP_EXTENDED_DAILY_MANAGEMENT,
            data_year=cls.academic_year
        )
        cls.url = reverse("learning_unit_prerequisite_update",
                          args=[cls.element_parent.id, cls.element_child.id])

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_permission_denied_when_no_permission(self):
        person_without_permission = PersonFactory()
        self.client.force_login(person_without_permission.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_not_found_when_learning_unit_not_contained_in_training(self):
        other_element = ElementGroupYearFactory(
            group_year__academic_year=self.academic_year,
            group_year__management_entity=self.element_parent.group_year.management_entity,
            group_year__education_group_type__category=education_group_categories.TRAINING,
            group_year__education_group_type__name=TrainingType.BACHELOR.name
        )
        url = reverse(
            "learning_unit_prerequisite_update",
            args=[other_element.id, self.learning_unit_year_child.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)

    def test_permission_denied_when_context_not_a_formation(self):
        group_element = ElementGroupYearFactory(
            group_year__academic_year=self.academic_year,
            group_year__education_group_type__group=True
        )
        PersonEntityFactory(person=self.person, entity=group_element.group_year.management_entity)
        url = reverse(
            "learning_unit_prerequisite_update",
            args=[group_element.id, self.element_child.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "learning_unit/tab_prerequisite_update.html")

    def test_context(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertEqual(context['root'], self.element_parent.group_year)

    @mock.patch("program_management.ddd.repositories._persist_prerequisite.persist")
    def test_post_data_simple_prerequisite(self, mock_persist):
        element_luy = ElementLearningUnitYearFactory(
            learning_unit_year__acronym='LSINF1111',
            learning_unit_year__academic_year=self.academic_year
        )
        GroupElementYearChildLeafFactory(
            parent_element=self.element_parent,
            child_element=element_luy
        )

        form_data = {
            "prerequisite_string": "LSINF1111"
        }
        response = self.client.post(self.url, data=form_data)

        redirect_url = reverse(
            "learning_unit_prerequisite",
            args=[self.element_parent.id, self.element_child.id]
        )
        self.assertRedirects(response, redirect_url)

        self.assertTrue(mock_persist.called)
