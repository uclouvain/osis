##############################################################################
#
#    OSIS stands for Open Student Information System. It"s an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
import datetime
from unittest import mock
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.contrib.auth.models import Permission

from base.models.enums import education_group_categories
from base.models.education_group_organization import EducationGroupOrganization
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.education_group_organization import EducationGroupOrganizationFactory
from base.tests.factories.entity import EntityFactory
from reference.tests.factories.country import CountryFactory
from base.tests.factories.user import UserFactory
from base.tests.factories.person import CentralManagerFactory
from base.tests.factories.organization import OrganizationFactory

DELETE_URL_NAME = "coorganization_delete"
EDIT_URL_NAME = "coorganization_edit"
CREATE_URL_NAME = "coorganization_create"

DIPLOMA = "UNIQUE"


class TestOrganizationViewPermission(TestCase):

    def setUp(self):
        today = datetime.date.today()
        academic_year = AcademicYearFactory(start_date=today, end_date=today.replace(year=today.year + 1),
                                            year=today.year)

        self.education_group_parent = EducationGroupYearFactory(acronym="Parent", academic_year=academic_year)
        self.education_group_child_1 = EducationGroupYearFactory(acronym="Child_1", academic_year=academic_year)
        self.person = CentralManagerFactory()
        self.person.user.user_permissions.add(Permission.objects.get(codename="can_access_education_group"))

        education_group_yr = EducationGroupYearFactory(
            academic_year=academic_year,
            education_group_type=EducationGroupTypeFactory(category=education_group_categories.TRAINING),
            management_entity=EntityFactory()
        )

        entity = EntityFactory(country=CountryFactory())
        organization = entity.organization
        EntityVersionFactory(entity=entity,
                             title="ROOT_V",
                             start_date=academic_year.start_date,
                             parent=None)
        education_group_organization = EducationGroupOrganizationFactory(
            organization=organization,
            education_group_year=education_group_yr,
            diploma=DIPLOMA,
            all_students=True,
        )
        self.education_group_organization_to_delete = EducationGroupOrganizationFactory(
            organization=OrganizationFactory()
        )
        self._set_urls(education_group_organization.id)
        self.client.force_login(self.person.user)

    def _set_urls(self, education_group_organization_id):
        self.url_create = reverse(CREATE_URL_NAME,
                                  args=[self.education_group_parent.id, self.education_group_child_1.id])
        self.url_edit = reverse(EDIT_URL_NAME,
                                args=[self.education_group_parent.id, self.education_group_child_1.id,
                                      education_group_organization_id])
        self.urls = [self.url_create,
                     self.url_edit,
                     reverse(DELETE_URL_NAME,
                             args=[
                                 self.education_group_parent.id,
                                 self.education_group_child_1.id,
                                 self.education_group_organization_to_delete.pk
                             ])
                     ]

    def test_when_not_logged(self):
        self.client.logout()
        for url in self.urls:
            response = self.client.get(url)
            self.assertRedirects(response, "/login/?next={}".format(url))

    def test_user_without_permission(self):
        an_other_user = UserFactory()
        PersonFactory(user=an_other_user)
        self.client.force_login(an_other_user)
        for url in self.urls:
            response = self.client.get(url)
            self.assertTemplateUsed(response, "access_denied.html")
            self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group", return_value=True)
    def test_user_with_permission(self, mock_permission):
        self.client.force_login(self.person.user)
        response = self.client.get(self.url_create)
        self.assertTemplateUsed(response, "education_group/organization_edit.html")

        response = self.client.get(self.url_edit)
        self.assertTemplateUsed(response, "education_group/organization_edit.html")


class TestOrganizationView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.person = PersonFactory(user=self.user)
        self.user.user_permissions.add(Permission.objects.get(codename="can_access_education_group"))

        today = datetime.date.today()
        self.academic_year = AcademicYearFactory(start_date=today,
                                                 end_date=today.replace(year=today.year + 1),
                                                 year=today.year)

        self.education_group_yr = EducationGroupYearFactory(
            academic_year=self.academic_year,
            education_group_type=EducationGroupTypeFactory(category=education_group_categories.TRAINING),
            management_entity=EntityFactory()
        )
        self.root_id = self.education_group_yr.id
        self._create_organization_and_entity()

    def _create_organization_and_entity(self):
        self.country_be = CountryFactory()
        self.organization = OrganizationFactory()
        entity = EntityFactory(country=self.country_be,
                               organization=self.organization)
        EntityVersionFactory(entity=entity,
                             start_date=self.academic_year.start_date,
                             end_date=None,
                             parent=None)

    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group", return_value=True)
    def test_create_get(self, mock_permissions):
        response = self.client.post(
            reverse(
                CREATE_URL_NAME,
                args=[
                    self.root_id,
                    self.education_group_yr.id,
                ]), data={}
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group", return_value=True)
    def test_create_post(self, mock_permissions):
        data = {
            "country": self.country_be.id,
            "organization": self.organization.id,
            "diploma": DIPLOMA,
            "all_students": "on",
        }
        response = self.client.post(
            reverse(
                CREATE_URL_NAME,
                args=[
                    self.root_id,
                    self.education_group_yr.id,
                ]), data=data
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        education_group_organization_created = EducationGroupOrganization.objects.all().first()
        self.assertEqual(education_group_organization_created.education_group_year_id, self.education_group_yr.id)
        self.assertEqual(education_group_organization_created.organization_id, data["organization"])
        self.assertEqual(education_group_organization_created.diploma, data["diploma"])
        self.assertTrue(education_group_organization_created.all_students)
        self.assertFalse(education_group_organization_created.enrollment_place)
        self.assertFalse(education_group_organization_created.is_producing_cerfificate)
        self.assertFalse(education_group_organization_created.is_producing_annexe)


class TestOrganizationDeleteView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.person = PersonFactory(user=self.user)
        self.user.user_permissions.add(Permission.objects.get(codename="can_access_education_group"))

        self.academic_year = create_current_academic_year()

        self.education_group_yr = EducationGroupYearFactory(
            academic_year=self.academic_year,
            education_group_type=EducationGroupTypeFactory(category=education_group_categories.TRAINING),
            management_entity=EntityFactory()
        )
        self.root_id = self.education_group_yr.id
        self.organization = OrganizationFactory()

    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group", return_value=True)
    def test_education_group_organization_delete_get(self, m):
        education_group_organization_to_delete = EducationGroupOrganizationFactory(organization=self.organization)

        response = self.client.get(
            reverse(DELETE_URL_NAME,
                    args=[
                        self.root_id,
                        self.education_group_yr.id,
                        education_group_organization_to_delete.pk
                    ])
        )
        self.assertTemplateUsed(response, "education_group/blocks/modal/modal_organization_confirm_delete_inner.html")

    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group", return_value=True)
    def test_education_group_organization_delete_post(self, m):
        education_group_organization_to_delete = EducationGroupOrganizationFactory(organization=self.organization)

        http_referer = reverse('education_group_read', args=[
            self.root_id,
            self.education_group_yr.id
        ]).rstrip('/') + "#panel_coorganization"

        response = self.client.post(
            reverse(
                DELETE_URL_NAME,
                args=[
                    self.root_id,
                    self.education_group_yr.id,
                    education_group_organization_to_delete.pk
                ]
            )
        )

        self.assertRedirects(response, http_referer, target_status_code=301)
        with self.assertRaises(EducationGroupOrganization.DoesNotExist):
            education_group_organization_to_delete.refresh_from_db()
