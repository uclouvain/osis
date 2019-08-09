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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime

from django.contrib.auth.models import Permission
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.test import TestCase
from django.urls import reverse

from attribution.models.attribution import Attribution
from attribution.tests.factories.attribution import AttributionFactory
from base.models.enums.education_group_types import TrainingType
from base.tests.factories import structure
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.business.entities import create_entities_hierarchy
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_manager import EntityManagerFactory
from base.tests.factories.group import EntityManagerGroupFactory, ProgramManagerGroupFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import UserFactory


class ScoresResponsibleSearchTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        group = EntityManagerGroupFactory()
        group.permissions.add(Permission.objects.get(codename='view_scoresresponsible'))
        group.permissions.add(Permission.objects.get(codename='change_scoresresponsible'))

        cls.tutor = TutorFactory()
        cls.user = cls.tutor.person.user
        cls.academic_year = AcademicYearFactory(year=datetime.date.today().year, start_date=datetime.date.today())

        # FIXME: Old structure model [To remove]
        cls.structure = structure.StructureFactory()
        cls.structure_children = structure.StructureFactory(part_of=cls.structure)

        # New structure model
        entities_hierarchy = create_entities_hierarchy()
        cls.root_entity = entities_hierarchy.get('root_entity')
        cls.child_one_entity = entities_hierarchy.get('child_one_entity')
        cls.child_two_entity = entities_hierarchy.get('child_two_entity')

        cls.entity_manager = EntityManagerFactory(
            person=cls.tutor.person,
            structure=cls.structure,
            entity=cls.root_entity,
        )

        cls.learning_unit_year = LearningUnitYearFactory(
            academic_year=cls.academic_year,
            acronym="LBIR1210",
            structure=cls.structure,
            learning_container_year__academic_year=cls.academic_year,
            learning_container_year__acronym="LBIR1210",
            learning_container_year__requirement_entity=cls.child_one_entity,
        )

        cls.learning_unit_year_children = LearningUnitYearFactory(
            academic_year=cls.academic_year,
            acronym="LBIR1211",
            structure=cls.structure_children,
            learning_container_year__academic_year=cls.academic_year,
            learning_container_year__acronym="LBIR1211",
            learning_container_year__requirement_entity=cls.child_two_entity,
        )

        cls.attribution = AttributionFactory(
            tutor=cls.tutor,
            learning_unit_year=cls.learning_unit_year,
            score_responsible=True
        )
        cls.attribution_children = AttributionFactory(
            tutor=cls.tutor,
            learning_unit_year=cls.learning_unit_year_children,
            score_responsible=True
        )

    def setUp(self):
        self.client.force_login(self.user)
        self.url = reverse('scores_responsible_list')

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'scores_responsible/list.html')

    def test_case_when_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_case_user_without_perms(self):
        unauthorized_user = UserFactory()
        self.client.force_login(unauthorized_user)

        response = self.client.get(self.url)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_case_search_without_filter_ensure_ordering(self):
        data = {
            'acronym': '',
            'learning_unit_title': '',
            'tutor': '',
            'scores_responsible': ''
        }
        response = self.client.get(self.url, data=data)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        qs_result = response.context['object_list']

        self.assertEqual(qs_result.count(), 2)
        self.assertEqual(qs_result[0], self.learning_unit_year)
        self.assertEqual(qs_result[1], self.learning_unit_year_children)

    def test_case_search_by_acronym_and_score_responsible(self):
        data = {
            'acronym': self.learning_unit_year.acronym,
            'learning_unit_title': '',
            'tutor': '',
            'scores_responsible': self.tutor.person.last_name
        }
        response = self.client.get(self.url, data=data)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        qs_result = response.context['object_list']

        self.assertEqual(qs_result.count(), 1)
        self.assertEqual(qs_result.first(), self.learning_unit_year)


class ScoresResponsibleManagementTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        group = EntityManagerGroupFactory()
        group_prgm = ProgramManagerGroupFactory()
        for g in [group, group_prgm]:
            g.permissions.add(Permission.objects.get(codename='view_scoresresponsible'))
            g.permissions.add(Permission.objects.get(codename='change_scoresresponsible'))

        cls.person = PersonFactory()
        cls.other_person = PersonFactory()
        cls.academic_year = AcademicYearFactory(year=datetime.date.today().year, start_date=datetime.date.today())

        # FIXME: Old structure model [To remove]
        cls.structure = structure.StructureFactory()

        entities_hierarchy = create_entities_hierarchy()
        cls.root_entity = entities_hierarchy.get('root_entity')

        cls.entity_manager = EntityManagerFactory(
            person=cls.person,
            structure=cls.structure,
            entity=cls.root_entity,
        )

        cls.learning_unit_year = LearningUnitYearFactory(
            academic_year=cls.academic_year,
            acronym="LBIR1210",
            structure=cls.structure,
            learning_container_year__academic_year=cls.academic_year,
            learning_container_year__acronym="LBIR1210",
            learning_container_year__requirement_entity=cls.root_entity,
        )
        cls.program = EducationGroupFactory()
        egy = EducationGroupYearFactory(
            education_group=cls.program,
            academic_year=cls.academic_year,
            education_group_type__name=TrainingType.BACHELOR.name,
            administration_entity=cls.root_entity
        )
        cls.program_manager = ProgramManagerFactory(
            person=cls.other_person,
            education_group=cls.program,
        )
        cls.group_element_year_2 = GroupElementYearFactory(
            parent=egy,
            child_branch=EducationGroupYearFactory(academic_year=cls.academic_year)
        )
        cls.group_element_year_2_1 = GroupElementYearFactory(
            parent=cls.group_element_year_2.child_branch,
            child_branch=None,
            child_leaf=cls.learning_unit_year
        )
        cls.other_entity = EntityFactory()
        cls.learning_unit_year_borrowed = LearningUnitYearFactory(
            academic_year=cls.academic_year,
            learning_container_year__academic_year=cls.academic_year,
            learning_container_year__requirement_entity=cls.other_entity,
        )
        cls.group_element_year_2_2 = GroupElementYearFactory(
            parent=cls.group_element_year_2.child_branch,
            child_branch=None,
            child_leaf=cls.learning_unit_year_borrowed
        )

    def setUp(self):
        self.client.force_login(self.person.user)
        self.url = reverse('scores_responsible_management')
        self.get_data = {
            'learning_unit_year': "learning_unit_year_%d" % self.learning_unit_year.pk
        }

    def test_case_when_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_case_user_without_perms(self):
        unauthorized_user = UserFactory()
        self.client.force_login(unauthorized_user)

        response = self.client.get(self.url, data=self.get_data)
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_case_user_which_cannot_managed_learning_unit_not_entity_managed(self):
        unauthorized_learning_unit_year = LearningUnitYearFactory()

        response = self.client.get(self.url, data={
            'learning_unit_year': "learning_unit_year_%d" % unauthorized_learning_unit_year.pk
        })
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_case_user_which_cannot_managed_learning_unit_borrowed_courses_as_program_manager(self):
        self.client.force_login(self.other_person.user)
        response = self.client.get(self.url, data={
            'learning_unit_year': "learning_unit_year_%d" % self.learning_unit_year_borrowed.pk
        })
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_assert_template_used(self):
        response = self.client.get(self.url, data=self.get_data)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'scores_responsible_edit.html')

    def test_assert_template_used_as_program_manager(self):
        self.client.force_login(self.other_person.user)
        response = self.client.get(self.url, data=self.get_data)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'scores_responsible_edit.html')


class ScoresResponsibleAddTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        group = EntityManagerGroupFactory()
        group.permissions.add(Permission.objects.get(codename='view_scoresresponsible'))
        group.permissions.add(Permission.objects.get(codename='change_scoresresponsible'))

        cls.person = PersonFactory()
        cls.academic_year = AcademicYearFactory(year=datetime.date.today().year, start_date=datetime.date.today())

        # FIXME: Old structure model [To remove]
        cls.structure = structure.StructureFactory()

        entities_hierarchy = create_entities_hierarchy()
        cls.root_entity = entities_hierarchy.get('root_entity')

        cls.entity_manager = EntityManagerFactory(
            person=cls.person,
            structure=cls.structure,
            entity=cls.root_entity,
        )
        cls.learning_unit_year = LearningUnitYearFactory(
            academic_year=cls.academic_year,
            acronym="LBIR1210",
            structure=cls.structure,
            learning_container_year__academic_year=cls.academic_year,
            learning_container_year__acronym="LBIR1210",
            learning_container_year__requirement_entity=cls.root_entity,
        )

    def setUp(self):
        attrib = AttributionFactory(learning_unit_year=self.learning_unit_year, score_responsible=False)
        self.url = reverse('scores_responsible_add', kwargs={'pk': self.learning_unit_year.pk})
        self.post_data = {
            'action': 'add',
            'attribution': "attribution_%d" % attrib.pk
        }
        self.client.force_login(self.person.user)

    def test_case_when_user_not_logged(self):
        self.client.logout()
        response = self.client.post(self.url, data=self.post_data)

        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_case_user_without_perms(self):
        unauthorized_user = UserFactory()
        self.client.force_login(unauthorized_user)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_case_add_score_responsibles(self):
        response = self.client.post(self.url, data=self.post_data)
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

        self.assertTrue(
            Attribution.objects.filter(learning_unit_year=self.learning_unit_year, score_responsible=True).exists()
        )
