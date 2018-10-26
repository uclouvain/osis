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

import datetime

from django.contrib.auth.models import Permission
from django.test import TestCase

from base.models.enums import education_group_categories
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory
from base.tests.factories.education_group_organization import EducationGroupOrganizationFactory
from base.tests.factories.entity import EntityFactory
from reference.tests.factories.country import CountryFactory
from base.forms.education_group.organization import OrganizationEditForm

DIPLOMA = "UNIQUE"


class TestOrganizationForm(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.person = PersonFactory(user=self.user)
        self.user.user_permissions.add(Permission.objects.get(codename="can_access_education_group"))

        today = datetime.date.today()
        self.academic_year = AcademicYearFactory(start_date=today, end_date=today.replace(year=today.year + 1),
                                                 year=today.year)

        self.education_group_yr = EducationGroupYearFactory(
            acronym='ARKE2A', academic_year=self.academic_year,
            education_group_type=EducationGroupTypeFactory(category=education_group_categories.TRAINING),
            management_entity=EntityFactory()
        )

        self.root_id = self.education_group_yr.id
        self.country_be = CountryFactory()

        self.entity = EntityFactory(country=self.country_be)
        self.organization = self.entity.organization
        EntityVersionFactory(entity=self.entity,
                             title="ROOT_V",
                             start_date=self.academic_year.start_date,
                             parent=None)
        self.education_group_organization = EducationGroupOrganizationFactory(
            organization=self.organization,
            education_group_year=self.education_group_yr,
            diploma=DIPLOMA,
            all_students=True,
        )

    def test_fields(self):
        entity_version = EntityVersionFactory()
        entity_version.refresh_from_db()
        form = OrganizationEditForm(None, instance=self.education_group_organization)
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
        self.assertEqual(form['country'].value(), self.entity.country.id)
        self.assertEqual(form['organization'].value(), self.education_group_organization.organization.id)
        self.assertEqual(form['diploma'].value(), DIPLOMA)
        self.assertTrue(form['all_students'].value())
        self.assertFalse(form['enrollment_place'].value())
        self.assertFalse(form['is_producing_cerfificate'].value())
        self.assertFalse(form['is_producing_annexe'].value())
