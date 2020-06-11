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
from django.test import TestCase

from base.models.enums.constraint_type import ConstraintTypeEnum
from base.models.enums.education_group_types import GroupType
from base.tests.factories.entity_version import EntityVersionFactory
from education_group.ddd.domain import exception
from education_group.ddd.domain._campus import Campus
from education_group.ddd.domain._content_constraint import ContentConstraint
from education_group.ddd.domain._remark import Remark
from education_group.ddd.domain._titles import Titles
from education_group.ddd.domain._entity import Entity as EntityValueObject
from education_group.ddd.domain.group import GroupIdentity, Group
from education_group.ddd.repository.group import GroupRepository
from education_group.tests.factories.group_year import GroupYearFactory


class TestGroupRepositoryGetMethod(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.management_entity_version = EntityVersionFactory(acronym='DRT')
        cls.group_year_db = GroupYearFactory(
            management_entity_id=cls.management_entity_version.entity_id
        )
        cls.group_identity = GroupIdentity(
            code=cls.group_year_db.partial_acronym,
            year=cls.group_year_db.academic_year.year,
        )

    def test_case_group_not_exists(self):
        dummy_group_identity = GroupIdentity(
            code="dummy-code",
            year=1966,
        )
        with self.assertRaises(exception.GroupNotFoundException):
            GroupRepository.get(dummy_group_identity)

    def test_fields_mapping(self):
        group = GroupRepository.get(self.group_identity)
        self.assertIsInstance(group, Group)

        self.assertEqual(group.entity_id, self.group_identity)
        self.assertEqual(group.type, GroupType[self.group_year_db.education_group_type.name])
        self.assertEqual(group.abbreviated_title, self.group_year_db.acronym)
        self.assertEqual(group.credits, self.group_year_db.credits)
        self.assertEqual(group.start_year, self.group_year_db.group.start_year.year)
        self.assertIsNone(group.end_year)

        self.assertIsInstance(group.titles, Titles)
        self.assertEqual(
            group.titles,
            Titles(title_fr=self.group_year_db.title_fr, title_en=self.group_year_db.title_en)
        )

        self.assertIsInstance(group.content_constraint, ContentConstraint)
        self.assertEqual(
            group.content_constraint,
            ContentConstraint(
                type=ConstraintTypeEnum[self.group_year_db.constraint_type],
                minimum=self.group_year_db.min_constraint,
                maximum=self.group_year_db.max_constraint
            )
        )

        self.assertIsInstance(group.management_entity, EntityValueObject)
        self.assertEqual(
            group.management_entity,
            EntityValueObject(
                acronym=self.management_entity_version.acronym,
            )
        )

        self.assertIsInstance(group.teaching_campus, Campus)
        self.assertEqual(
            group.teaching_campus,
            Campus(
                name=self.group_year_db.main_teaching_campus.name,
                university_name=self.group_year_db.main_teaching_campus.organization.name,
            )
        )

        self.assertIsInstance(group.remark, Remark)
        self.assertEqual(
            group.remark,
            Remark(
                text_fr=self.group_year_db.remark_fr,
                text_en=self.group_year_db.remark_en
            )
        )
