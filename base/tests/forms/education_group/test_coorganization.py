##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.contrib.auth.models import Permission
from django.test import TestCase

from base.models.enums import education_group_categories, diploma_coorganization
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.organization_address import OrganizationAddressFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory
from base.tests.factories.education_group_organization import EducationGroupOrganizationFactory
from base.tests.factories.entity import EntityFactory
from reference.tests.factories.country import CountryFactory
from base.forms.education_group.coorganization import CoorganizationEditForm


class TestCoorganizationForm(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.person = PersonFactory(user=self.user)
        self.user.user_permissions.add(Permission.objects.get(codename="can_access_education_group"))

        self.academic_year = create_current_academic_year()
        self.education_group_yr = EducationGroupYearFactory(
            acronym='ARKE2A', academic_year=self.academic_year,
            education_group_type=EducationGroupTypeFactory(category=education_group_categories.TRAINING),
            management_entity=EntityFactory()
        )

        self.root_id = self.education_group_yr.id
        self.country_be = CountryFactory()

        self.organization_address = OrganizationAddressFactory(country=self.country_be)
        self.organization = self.organization_address.organization
        self.education_group_organization = EducationGroupOrganizationFactory(
            organization=self.organization,
            education_group_year=self.education_group_yr,
            diploma=diploma_coorganization.UNIQUE,
            all_students=True,
        )

    def test_fields(self):
        form = CoorganizationEditForm(None, instance=self.education_group_organization)
        expected_fields = [
            'country',
            'organization',
            'all_students',
            'enrollment_place',
            'diploma',
            'is_producing_cerfificate',
            'is_producing_annexe',
        ]
        actual_fields = list(form.fields.keys())

        self.assertListEqual(expected_fields, actual_fields)
        self.assertEqual(form['country'].value(), self.organization_address.country.pk)
        self.assertEqual(form['organization'].value(), self.education_group_organization.organization.pk)
        self.assertEqual(form['diploma'].value(), diploma_coorganization.UNIQUE)
        self.assertTrue(form['all_students'].value())
        self.assertFalse(form['enrollment_place'].value())
        self.assertFalse(form['is_producing_cerfificate'].value())
        self.assertFalse(form['is_producing_annexe'].value())
