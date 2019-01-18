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
from django.test import TestCase

from base.business.group_element_years.management import is_max_child_reached, is_min_child_reached, \
    compute_number_children
from base.models.enums.link_type import LinkTypes
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.authorized_relationship import AuthorizedRelationshipFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory


class TestChildReachedMixin():
    @classmethod
    def setUpTestData(cls):
        cls.parent_type = EducationGroupTypeFactory()
        cls.child_type = EducationGroupTypeFactory()

        cls.parent_egy = EducationGroupYearFactory(education_group_type=cls.parent_type)
        cls.child_egy = EducationGroupYearFactory(education_group_type=cls.child_type)

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


class TestIsMaxChildReached(TestChildReachedMixin, TestCase):
    def test_when_no_authorized_relationship(self):
        self.assertTrue(is_max_child_reached(self.parent_egy, self.child_egy.education_group_type))

    def test_should_return_false_if_no_group_element_years_of_child_type_and_max_count_set_to_one(self):
        GroupElementYearFactory(parent=self.parent_egy)
        self.create_authorized_relationship(max_count=1)
        self.assertFalse(is_max_child_reached(self.parent_egy, self.child_egy.education_group_type))

    def test_should_return_false_if_no_group_element_years_child_type_and_max_count_set_to_many(self):
        self.create_authorized_relationship(max_count=None)
        self.assertFalse(is_max_child_reached(self.parent_egy, self.child_egy.education_group_type))

    def test_should_return_true_if_one_group_element_years_child_type_and_max_count_set_to_one(self):
        self.create_group_element_years_of_child_type()
        self.create_authorized_relationship(max_count=1)
        self.assertTrue(is_max_child_reached(self.parent_egy, self.child_egy.education_group_type))

    def test_should_return_false_if_multiple_group_element_years_of_child_type_and_max_count_set_to_many(self):
        self.create_group_element_years_of_child_type()
        self.create_group_element_years_of_child_type()
        self.create_authorized_relationship(max_count=None)
        self.assertFalse(is_max_child_reached(self.parent_egy, self.child_egy.education_group_type))

    def test_with_reference_link(self):
        self.create_authorized_relationship(max_count=3)

        ref_group = self.create_group_element_years_of_child_type(link_type=LinkTypes.REFERENCE.name)
        self.create_group_element_years_of_child_type(parent=ref_group.child_branch)
        self.assertFalse(is_max_child_reached(self.parent_egy, self.child_egy.education_group_type))

        self.create_group_element_years_of_child_type(parent=ref_group.child_branch)
        self.assertTrue(is_max_child_reached(self.parent_egy, self.child_egy.education_group_type))


class TestIsMinChildReached(TestChildReachedMixin, TestCase):
    def test_when_no_authorized_relationship(self):
        self.assertTrue(is_min_child_reached(self.parent_egy, self.child_egy.education_group_type))

    def test_should_return_true_if_no_group_element_years_of_child_type_and_min_count_set_to_zero(self):
        GroupElementYearFactory(parent=self.parent_egy)
        self.create_authorized_relationship(min_count=0)
        self.assertFalse(is_min_child_reached(self.parent_egy, self.child_egy.education_group_type))

    def test_should_return_true_if_no_group_element_years_child_type_and_min_count_set_to_one(self):
        self.create_authorized_relationship(min_count=1)
        self.assertTrue(is_min_child_reached(self.parent_egy, self.child_egy.education_group_type))

    def test_should_return_false_if_one_group_element_year_of_child_type_and_min_count_set_to_zero(self):
        self.create_group_element_years_of_child_type()
        self.create_authorized_relationship(min_count=0)
        self.assertFalse(is_min_child_reached(self.parent_egy, self.child_egy.education_group_type))

    def test_should_return_true_if_one_group_element_years_of_child_type_and_min_count_set_to_one(self):
        self.create_group_element_years_of_child_type()
        self.create_authorized_relationship(min_count=1)
        self.assertTrue(is_min_child_reached(self.parent_egy, self.child_egy.education_group_type))

    def test_should_return_false_if_multiple_group_element_years_of_child_type_and_min_count_set_to_one(self):
        self.create_group_element_years_of_child_type()
        self.create_group_element_years_of_child_type()
        self.create_authorized_relationship(min_count=1)
        self.assertFalse(is_min_child_reached(self.parent_egy, self.child_egy.education_group_type))

    def test_with_reference_link(self):
        self.create_authorized_relationship(min_count=2)

        ref_group = self.create_group_element_years_of_child_type(link_type=LinkTypes.REFERENCE.name)
        self.assertTrue(is_min_child_reached(self.parent_egy, self.child_egy.education_group_type))

        self.create_group_element_years_of_child_type(parent=ref_group.child_branch)
        self.assertTrue(is_min_child_reached(self.parent_egy, self.child_egy.education_group_type))

        self.create_group_element_years_of_child_type(parent=ref_group.child_branch)
        self.assertFalse(is_min_child_reached(self.parent_egy, self.child_egy.education_group_type))


class TestComputeNumberChildren(TestCase):
    def test_when_no_children(self):
        parent_without_children = EducationGroupYearFactory()
        child = EducationGroupYearFactory()

        expected_result = {
            child.education_group_type.id: 1
        }
        self.assertDictEqual(expected_result, compute_number_children(parent_without_children, child, None))

    def test_when_children_of_same_education_group_type_of_link_main(self):
        parent_egy = EducationGroupYearFactory()
        children_education_group_type = EducationGroupTypeFactory()
        [GroupElementYearFactory(parent=parent_egy, child_branch__education_group_type=children_education_group_type)
         for _ in range(3)]

        child = EducationGroupYearFactory(education_group_type=children_education_group_type)

        expected_result = {
            children_education_group_type.id: 4
        }
        self.assertEqual(
            expected_result,
            compute_number_children(parent_egy, child, None)
        )

    def test_when_children_of_different_education_group_type_of_link_main(self):
        parent_egy = EducationGroupYearFactory()
        children_education_group_type_1 = EducationGroupTypeFactory()
        children_education_group_type_2 = EducationGroupTypeFactory()
        [GroupElementYearFactory(parent=parent_egy, child_branch__education_group_type=children_education_group_type_1)
         for _ in range(3)]
        [GroupElementYearFactory(parent=parent_egy, child_branch__education_group_type=children_education_group_type_2)
         for _ in range(1)]

        child = EducationGroupYearFactory(education_group_type=children_education_group_type_2)

        expected_result = {
            children_education_group_type_1.id: 3,
            children_education_group_type_2.id: 2
        }
        self.assertEqual(
            expected_result,
            compute_number_children(parent_egy, child, None)
        )

    def test_when_children_with_link_main_reference(self):
        parent_egy = EducationGroupYearFactory()
        children_education_group_type_1 = EducationGroupTypeFactory()
        [GroupElementYearFactory(parent=parent_egy, child_branch__education_group_type=children_education_group_type_1)
         for _ in range(3)]

        reference_group_element_year = GroupElementYearFactory(parent=parent_egy, link_type=LinkTypes.REFERENCE.name)

        children_education_group_type_2 = EducationGroupTypeFactory()
        [GroupElementYearFactory(parent=reference_group_element_year.child_branch,
                                 child_branch__education_group_type=children_education_group_type_2)
         for _ in range(2)]

        child = EducationGroupYearFactory(education_group_type=children_education_group_type_2)

        expected_result = {
            children_education_group_type_1.id: 3,
            children_education_group_type_2.id: 3
        }
        self.assertEqual(
            expected_result,
            compute_number_children(parent_egy, child, None)
        )

    def test_when_children_of_different_education_group_type_of_link_main_and_reference(self):
        parent_egy = EducationGroupYearFactory()
        children_education_group_type_1 = EducationGroupTypeFactory()
        children_education_group_type_2 = EducationGroupTypeFactory()
        [GroupElementYearFactory(parent=parent_egy, child_branch__education_group_type=children_education_group_type_1)
         for _ in range(3)]
        [GroupElementYearFactory(parent=parent_egy, child_branch__education_group_type=children_education_group_type_2)
         for _ in range(1)]

        child = EducationGroupYearFactory(education_group_type=children_education_group_type_2)
        children_education_group_type_3 = EducationGroupTypeFactory()
        [GroupElementYearFactory(parent=child, child_branch__education_group_type=children_education_group_type_3)
         for _ in range(2)]

        expected_result = {
            children_education_group_type_1.id: 3,
            children_education_group_type_2.id: 1,
            children_education_group_type_3.id: 2
        }
        self.assertEqual(
            expected_result,
            compute_number_children(parent_egy, child, LinkTypes.REFERENCE.name)
        )

    def test_when_switching_existing_children(self):
        parent_egy = EducationGroupYearFactory()
        children_education_group_type_1 = EducationGroupTypeFactory()
        children_education_group_type_2 = EducationGroupTypeFactory()
        [GroupElementYearFactory(parent=parent_egy, child_branch__education_group_type=children_education_group_type_1)
         for _ in range(3)]
        [GroupElementYearFactory(parent=parent_egy, child_branch__education_group_type=children_education_group_type_2)
         for _ in range(1)]

        grp = GroupElementYearFactory(parent=parent_egy)
        child = grp.child_branch
        children_education_group_type_3 = EducationGroupTypeFactory()
        [GroupElementYearFactory(parent=child, child_branch__education_group_type=children_education_group_type_3)
         for _ in range(2)]

        expected_result = {
            children_education_group_type_1.id: 3,
            children_education_group_type_2.id: 1,
            children_education_group_type_3.id: 2
        }
        self.assertEqual(
            expected_result,
            compute_number_children(parent_egy, child, LinkTypes.REFERENCE.name)
        )
