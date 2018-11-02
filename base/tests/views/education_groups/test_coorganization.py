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
from unittest import mock
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponseForbidden

from base.models.enums import diploma_coorganization
from base.models.education_group_organization import EducationGroupOrganization
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.education_group_year import TrainingFactory
from base.tests.factories.organization_address import OrganizationAddressFactory
from base.tests.factories.education_group_organization import EducationGroupOrganizationFactory
from base.tests.factories.person import CentralManagerFactory
from base.tests.factories.organization import OrganizationFactory

DELETE_URL_NAME = "coorganization_delete"
EDIT_URL_NAME = "coorganization_edit"
CREATE_URL_NAME = "coorganization_create"


class CoorganizationViewSetupTest(TestCase):
    def setUp(self):
        self.academic_year = create_current_academic_year()
        self.person = CentralManagerFactory("can_access_education_group")

        # Create an organization with main address
        self.organization = OrganizationFactory()
        self.main_organization_address = OrganizationAddressFactory(
            organization=self.organization,
            is_main=True
        )

        # Create Training which is co-organized
        self.training_egy = TrainingFactory(academic_year=self.academic_year)
        self.education_group_organization = EducationGroupOrganizationFactory(
            organization=self.organization,
            education_group_year= self.training_egy,
            diploma=diploma_coorganization.UNIQUE,
            all_students=True,
        )
        self.client.force_login(self.person.user)


class TestCoorganizationCreateView(CoorganizationViewSetupTest):
    def setUp(self):
        super().setUp()
        self.url_create = reverse(
            CREATE_URL_NAME,
            args=[self.training_egy.pk, self.training_egy.pk]
        )

    def test_when_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url_create)
        self.assertRedirects(response, "/login/?next={}".format(self.url_create))

    def test_user_without_permission(self):
        # Remove permission
        self.person.user.user_permissions.clear()

        response = self.client.get(self.url_create)
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group", return_value=True)
    def test_assert_template_used(self, mock_permissions):
        response = self.client.get(self.url_create)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "education_group/organization_edit.html")

    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group", return_value=True)
    def test_create_post(self, mock_permissions):
        # Remove current
        self.education_group_organization.delete()

        data = {
            "country": self.main_organization_address.country.pk,
            "organization": self.organization.id,
            "diploma": diploma_coorganization.NOT_CONCERNED,
            "all_students": "on",
        }
        response = self.client.post(self.url_create, data=data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        # Check into database for created value
        education_group_organization_created = EducationGroupOrganization.objects.get(
            education_group_year_id=self.training_egy.id
        )
        self.assertEqual(education_group_organization_created.organization_id, data["organization"])
        self.assertEqual(education_group_organization_created.diploma, data["diploma"])
        self.assertTrue(education_group_organization_created.all_students)
        self.assertFalse(education_group_organization_created.enrollment_place)
        self.assertFalse(education_group_organization_created.is_producing_cerfificate)
        self.assertFalse(education_group_organization_created.is_producing_annexe)


class TestCoorganizationUpdateView(CoorganizationViewSetupTest):
    def setUp(self):
        super().setUp()
        self.url_edit = reverse(
            EDIT_URL_NAME,
            args=[self.training_egy.id, self.training_egy.id, self.education_group_organization.pk]
        )

    def test_when_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url_edit)
        self.assertRedirects(response, "/login/?next={}".format(self.url_edit))

    def test_user_without_permission(self):
        # Remove permission
        self.person.user.user_permissions.clear()

        response = self.client.get(self.url_edit)
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group", return_value=True)
    def test_assert_template_used(self, mock_permissions):
        response = self.client.get(self.url_edit)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "education_group/organization_edit.html")


class TestCoorganizationDeleteView(CoorganizationViewSetupTest):
    def setUp(self):
        super().setUp()
        self.url_delete = reverse(
            DELETE_URL_NAME,
            args=[
                self.training_egy.id,
                self.training_egy.id,
                self.education_group_organization.pk
            ]
        )

    def test_when_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url_delete)
        self.assertRedirects(response, "/login/?next={}".format(self.url_delete))

    def test_user_without_permission(self):
        # Remove permission
        self.person.user.user_permissions.clear()

        response = self.client.get(self.url_delete)
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group", return_value=True)
    def test_template_used(self, mock_permission):
        response = self.client.get(self.url_delete)
        self.assertTemplateUsed(response, "education_group/blocks/modal/modal_organization_confirm_delete_inner.html")

    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group", return_value=True)
    def test_education_group_organization_delete_post_redirection(self, mock_permissions):
        http_referer = reverse('education_group_read', args=[
            self.training_egy.pk,
            self.training_egy.pk,
        ]).rstrip('/') + "#panel_coorganization"

        response = self.client.post(self.url_delete)

        self.assertRedirects(response, http_referer, target_status_code=301)
        with self.assertRaises(EducationGroupOrganization.DoesNotExist):
            self.education_group_organization.refresh_from_db()
