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
import datetime

from django.db.models import Case, When, F, CharField
from django.test import TestCase

from base.tests.factories.academic_year import get_current_year
from base.tests.factories.education_group_publication_contact import EducationGroupPublicationContactFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from program_management.tests.ddd.factories.node import NodeGroupYearFactory
from webservices.api.serializers.contacts import ContactsSerializer, ContactSerializer


class ContactsSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_year = get_current_year()
        cls.language = 'en'
        now = datetime.datetime.now()
        cls.entity = EntityFactory()
        EntityVersionFactory(
            entity=cls.entity,
            start_date=now.replace(year=now.year - 1)
        )
        cls.egy = EducationGroupYearFactory(
            academic_year__year=now.year,
            management_entity=cls.entity,
            publication_contact_entity=cls.entity
        )
        cls.node = NodeGroupYearFactory(code=cls.egy.partial_acronym, year=now.year)
        cls.serializer = ContactsSerializer(cls.node, context={'language': cls.language, 'offer': cls.egy})

    def test_contains_expected_fields(self):
        expected_fields = [
            'contacts',
            'text',
            'entity',
            'management_entity'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_return_none_if_no_pubication_contact_entity(self):
        egy = EducationGroupYearFactory(
            academic_year__year=self.current_year,
            management_entity=self.entity,
            publication_contact_entity=None
        )
        node = NodeGroupYearFactory(code=egy.partial_acronym, year=self.current_year)
        serializer = ContactsSerializer(node, context={'language': self.language, 'offer': egy})
        self.assertIsNone(serializer.data['entity'])


class ContactSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.language = 'en'
        cls.egy = EducationGroupYearFactory()
        cls.contact = EducationGroupPublicationContactFactory(education_group_year=cls.egy)
        cls.annoted_contact = cls.egy.educationgrouppublicationcontact_set.all().annotate(
            description_or_none=Case(
                When(description__exact='', then=None),
                default=F('description'),
                output_field=CharField()
            ),
            translated_role=Case(
                When(role_fr__exact='', then=None),
                default=F('role_fr'),
                output_field=CharField()
            ),
        ).first()
        cls.serializer = ContactSerializer(cls.annoted_contact, context={'language': cls.language, 'offer': cls.egy})

    def test_contains_expected_fields(self):
        expected_fields = [
            'description',
            'email',
            'role'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)
