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
import random
from unittest import skip

from django.conf import settings
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from waffle.testutils import override_flag, override_switch

from backoffice.settings.base import LANGUAGE_CODE_EN
from base.models.enums.education_group_types import TrainingType
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_type import TrainingEducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory, EducationGroupYearBachelorFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.person import CentralManagerForUEFactory, PersonFactory, FacultyManagerForUEFactory
from base.tests.factories.user import SuperUserFactory
from education_group.tests.factories.group_year import GroupYearFactory
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.models.education_group_version import EducationGroupVersion
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionIdentityFactory, \
    ProgramTreeVersionFactory, StandardProgramTreeVersionFactory
from program_management.views.tree_version.create import CreateProgramTreeVersionType


class TestCreateProgramTreeVersion(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(current=True)
        cls.year = cls.academic_year.year
        cls.entity_identity = ProgramTreeVersionIdentityFactory(year=cls.year, version_name="VERSION")
        cls.type = TrainingEducationGroupTypeFactory()
        cls.database_offer = EducationGroupYearFactory(
            academic_year=cls.academic_year,
            education_group_type=cls.type,
            acronym=cls.entity_identity.offer_acronym,
        )
        cls.repository = ProgramTreeVersionRepository()
        cls.new_program_tree = ProgramTreeFactory(
            root_node__year=cls.year,
            root_node__start_year=cls.year,
            root_node__end_year=cls.year,
            root_node__node_type=TrainingType[cls.type.name],
        )
        cls.new_program_tree_version = StandardProgramTreeVersionFactory(
            entity_identity=cls.entity_identity,
            entity_id=cls.entity_identity,
            program_tree_identity=cls.new_program_tree.entity_id,
            tree=cls.new_program_tree,
        )
        GroupYearFactory(
            partial_acronym=cls.new_program_tree_version.program_tree_identity.code,
            academic_year__year=cls.year
        )
        cls.repository.create(cls.new_program_tree_version)
        cls.standard_version = EducationGroupVersion.objects.get(
            offer__acronym=cls.new_program_tree_version.entity_id.offer_acronym,
            offer__academic_year__year=cls.new_program_tree_version.entity_id.year,
            version_name=cls.new_program_tree_version.entity_id.version_name,
            is_transition=cls.new_program_tree_version.entity_id.is_transition
        )
        cls.url = reverse(
            "create_education_group_version",
            kwargs={
                "year": cls.new_program_tree_version.entity_id.year,
                "code": cls.new_program_tree_version.entity_id.offer_acronym
            }
        )
        cls.central_manager = CentralManagerForUEFactory("view_educationgroup")
        cls.factulty_manager = FacultyManagerForUEFactory("view_educationgroup")
        cls.simple_user = PersonFactory()
        cls.valid_data = {
                "version_name": "CMS",
                "title": "Titre",
                "title_english": "Title",
                "end_year": cls.year,
                "save_type": CreateProgramTreeVersionType.NEW_VERSION.value
            }

    def test_get_init_form_create_program_tree_version_with_disconected_user(self):
        response = self.client.get(self.url, data={}, follow=True)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_get_init_form_create_program_tree_version_for_central_manager(self):
        self.client.force_login(self.central_manager.user)
        response = self.client.get(self.url, data={}, follow=True)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "tree_version/create_specific_version_inner.html")

    def test_get_init_form_create_program_tree_version_for_faculty_manager(self):
        self.client.force_login(self.factulty_manager.user)
        response = self.client.get(self.url, data={}, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_get_init_form_create_program_tree_version_for_simple_user(self):
        self.client.force_login(self.simple_user.user)
        response = self.client.get(self.url, data={}, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_get_context_form(self):
        self.client.force_login(self.central_manager.user)
        response = self.client.get(self.url, data={}, follow=True)
        self.assertEqual(len(response.context['form'].fields['end_year'].choices), 8)
        self.assertEqual(response.context['form'].fields['end_year'].choices[0][0], None)
        self.assertEqual(response.context['form'].fields['end_year'].choices[7][0], self.year+6)
        self.assertEqual(response.context['form'].fields['end_year'].initial, None)
