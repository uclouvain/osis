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
###########################################################################
from unittest import mock

from django.test import TestCase

from base.business.group_element_years.management import compute_number_children_by_education_group_type, \
    check_min_max_child_reached
from base.models.authorized_relationship import AuthorizedRelationship
from base.models.enums.link_type import LinkTypes
from base.models.exceptions import MaxChildrenReachedException, MinChildrenReachedException
from base.tests.factories.authorized_relationship import AuthorizedRelationshipFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory, GroupElementYearChildLeafFactory


class TestCheckMinMaxChildReached(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent_type = EducationGroupTypeFactory()
        cls.child_type, cls.other_child_type = EducationGroupTypeFactory.create_batch(2)

        cls.parent_egy = EducationGroupYearFactory(education_group_type=cls.parent_type)
        cls.child_egy = EducationGroupYearFactory(education_group_type=cls.child_type)

    def setUp(self):
        returned_value = {
            self.child_type.name: 2
        }
        self.mocked_compute_number_children = mock.patch(
            "base.business.group_element_years.management.compute_number_children_by_education_group_type",
            return_value=returned_value
        )
        self.mocked_perm = self.mocked_compute_number_children.start()

        self.addCleanup(self.mocked_compute_number_children.stop)

    def create_group_element_years_of_child_type(self, parent=None, link_type=None):
        return GroupElementYearFactory(
            parent=parent or self.parent_egy,
            link_type=link_type,
            child_branch__education_group_type=self.child_type
        )

    def create_authorized_relationship(self, max_count=None, min_count=0):
        return AuthorizedRelationshipFactory(
            parent_type=self.parent_type,
            child_type=self.child_type,
            max_count_authorized=max_count,
            min_count_authorized=min_count,
        )

    def test_when_no_authorized_relationship(self):
        with self.assertRaises(AuthorizedRelationship.DoesNotExist):
            check_min_max_child_reached(self.parent_egy, self.child_egy, self.child_type)

    def test_should_raise_exception_when_max_count_exceeded(self):
        self.create_authorized_relationship(max_count=1)

        with self.assertRaises(MaxChildrenReachedException):
            check_min_max_child_reached(self.parent_egy, self.child_egy, self.child_type)

    def test_should_raise_exception_when_min_count_subceeded(self):
        self.create_authorized_relationship(min_count=3)

        with self.assertRaises(MinChildrenReachedException):
            check_min_max_child_reached(self.parent_egy, self.child_egy, self.child_type)

    def test_when_limit_respected(self):
        self.create_authorized_relationship()
        self.assertIsNone(check_min_max_child_reached(self.parent_egy, self.child_egy, self.child_type))


class TestComputeNumberChildrenByEducationGroupType(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent_egy = EducationGroupYearFactory()
        cls.education_group_types = EducationGroupTypeFactory.create_batch(3)
        GroupElementYearFactory.create_batch(
            3,
            parent=cls.parent_egy,
            child_branch__education_group_type=cls.education_group_types[0]
        )
        GroupElementYearFactory.create_batch(
            2,
            parent=cls.parent_egy,
            child_branch__education_group_type=cls.education_group_types[1]
        )
        GroupElementYearChildLeafFactory.create_batch(
            2,
            parent=cls.parent_egy
        )

        cls.reference_group_element_year_children = GroupElementYearFactory(
            parent=cls.parent_egy,
            child_branch__education_group_type=cls.education_group_types[0],
            link_type=LinkTypes.REFERENCE.name
        )
        GroupElementYearFactory.create_batch(
            2,
            parent=cls.reference_group_element_year_children.child_branch,
            child_branch__education_group_type=cls.education_group_types[1]
        )
        GroupElementYearFactory(
            parent=cls.reference_group_element_year_children.child_branch,
            child_branch__education_group_type=cls.education_group_types[2]
        )

        cls.child = EducationGroupYearFactory(education_group_type=cls.education_group_types[0])
        GroupElementYearFactory.create_batch(
            2,
            parent=cls.child,
            child_branch__education_group_type=cls.education_group_types[2]
        )

    def test_when_no_children(self):
        parent_without_children = EducationGroupYearFactory()

        expected_result = {
            self.education_group_types[0].name: 1
        }

        old_link = None
        new_link = GroupElementYearFactory.build(child_branch=self.child, link_type=None)
        self.assertDictEqual(
            expected_result,
            compute_number_children_by_education_group_type(parent_without_children, old_link, new_link)
        )

    def test_when_children(self):
        expected_result = {
            self.education_group_types[0].name: 3 + 1,
            self.education_group_types[1].name: 4,
            self.education_group_types[2].name: 1
        }
        old_link = None
        new_link = GroupElementYearFactory.build(child_branch=self.child, link_type=None)
        self.assertDictEqual(
            expected_result,
            compute_number_children_by_education_group_type(self.parent_egy, old_link, new_link)
        )

    def test_when_children_with_link_reference(self):
        expected_result = {
            self.education_group_types[0].name: 3,
            self.education_group_types[1].name: 4,
            self.education_group_types[2].name: 1 + 2
        }
        old_link = None
        new_link = GroupElementYearFactory.build(child_branch=self.child, link_type=LinkTypes.REFERENCE.name)
        self.assertDictEqual(
            expected_result,
            compute_number_children_by_education_group_type(self.parent_egy, old_link, new_link)
        )

    def test_when_switching_link_type_of_existing_child(self):
        expected_result = {
            self.education_group_types[0].name: 3 + 1,
            self.education_group_types[1].name: 4 - 2,
            self.education_group_types[2].name: 1 - 1
        }
        old_link = self.reference_group_element_year_children
        new_link = GroupElementYearFactory.build(child_branch=self.reference_group_element_year_children.child_branch,
                                                 link_type=None)
        self.assertDictEqual(
            expected_result,
            compute_number_children_by_education_group_type(self.parent_egy, old_link, new_link)
        )
