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
from django.test import TestCase

from base.business.education_groups import delete
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import GroupType
from base.models.group_element_year import GroupElementYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.authorized_relationship import AuthorizedRelationshipFactory
from base.tests.factories.education_group_year import TrainingFactory, GroupFactory
from base.tests.factories.group_element_year import GroupElementYearFactory


class TestHaveContents(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2019)

    def test_have_contents_case_no_contents(self):
        education_group_year = TrainingFactory(academic_year=self.academic_year)
        self.assertFalse(delete._have_contents_which_are_not_mandatory(education_group_year))

    def test_have_contents_case_no_contents_which_because_mandatory_structure(self):
        """
        In this test, we ensure that all of his children are mandatory groups and they are empty.
        It must be consider as empty
        """
        education_group_year = TrainingFactory(academic_year=self.academic_year)
        for education_group_type in [GroupType.COMMON_CORE.name, GroupType.FINALITY_120_LIST_CHOICE.name]:
            child = GroupFactory(academic_year=self.academic_year, education_group_type__name=education_group_type)

            AuthorizedRelationshipFactory(
                parent_type=education_group_year.education_group_type,
                child_type=child.education_group_type,
                min_count_authorized=1,
            )
            GroupElementYearFactory(parent=education_group_year, child_branch=child)
        self.assertFalse(delete._have_contents_which_are_not_mandatory(education_group_year))

    def test_have_contents_case_have_contents_because_mandatory_structure_is_present_multiple_times(self):
        """
        In this test, we ensure that we have two elements of one type which are mandatory in the basic structure.
        ==> We must consider as it have contents
        """
        education_group_year = TrainingFactory(academic_year=self.academic_year)
        subgroup_1 = GroupFactory(academic_year=self.academic_year, education_group_type__name=GroupType.SUB_GROUP.name)
        GroupElementYearFactory(parent=education_group_year, child_branch=subgroup_1)

        subgroup_2 = GroupFactory(
            academic_year=self.academic_year,
            education_group_type=subgroup_1.education_group_type,
        )
        GroupElementYearFactory(parent=education_group_year, child_branch=subgroup_2)

        AuthorizedRelationshipFactory(
            parent_type=education_group_year.education_group_type,
            child_type=subgroup_1.education_group_type,
            min_count_authorized=1,
        )
        self.assertTrue(delete._have_contents_which_are_not_mandatory(education_group_year))

    def test_have_contents_case_contents_because_structure_have_child_which_are_not_mandatory(self):
        """
        In this test, we ensure that at least one children are not mandatory groups so they must not be considered
        as empty
        """
        education_group_year = TrainingFactory(academic_year=self.academic_year)

        child_mandatory = GroupFactory(academic_year=self.academic_year)
        AuthorizedRelationshipFactory(
            parent_type=education_group_year.education_group_type,
            child_type=child_mandatory.education_group_type,
            min_count_authorized=1
        )
        GroupElementYearFactory(parent=education_group_year, child_branch=child_mandatory)

        child_no_mandatory = GroupFactory(academic_year=self.academic_year)
        AuthorizedRelationshipFactory(
            parent_type=education_group_year.education_group_type,
            child_type=child_mandatory.education_group_type,
            min_count_authorized=0
        )
        GroupElementYearFactory(parent=education_group_year, child_branch=child_no_mandatory)
        self.assertTrue(delete._have_contents_which_are_not_mandatory(education_group_year))


class TestRunDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2019)

    def test_delete_case_no_mandatory_structure(self):
        education_group_year = TrainingFactory(academic_year=self.academic_year)
        delete.start(education_group_year)

        with self.assertRaises(EducationGroupYear.DoesNotExist):
            EducationGroupYear.objects.get(pk=education_group_year.pk)

    def test_delete_case_remove_mandatory_structure(self):
        education_group_year = TrainingFactory(academic_year=self.academic_year)

        child_mandatory = GroupFactory(
            academic_year=self.academic_year,
            education_group_type__name=GroupType.COMMON_CORE.name
        )
        AuthorizedRelationshipFactory(
            parent_type=education_group_year.education_group_type,
            child_type=child_mandatory.education_group_type,
            min_count_authorized=1,
        )
        link_parent_child = GroupElementYearFactory(parent=education_group_year, child_branch=child_mandatory)

        delete.start(education_group_year)
        with self.assertRaises(EducationGroupYear.DoesNotExist):
            EducationGroupYear.objects.get(pk=education_group_year.pk)
        with self.assertRaises(EducationGroupYear.DoesNotExist):
            EducationGroupYear.objects.get(pk=child_mandatory.pk)
        with self.assertRaises(GroupElementYear.DoesNotExist):
            GroupElementYear.objects.get(pk=link_parent_child.pk)

    def test_delete_case_remove_mandatory_structure_case_reused_item_which_are_mandatory(self):
        """
        In this test, we ensure that the mandatory elem is not removed if it is reused in another structure
        """
        education_group_year = TrainingFactory(academic_year=self.academic_year)

        child_mandatory = GroupFactory(
            academic_year=self.academic_year,
            education_group_type__name=GroupType.COMMON_CORE.name
        )
        AuthorizedRelationshipFactory(
            parent_type=education_group_year.education_group_type,
            child_type=child_mandatory.education_group_type,
            min_count_authorized=1,
        )
        link_parent_child = GroupElementYearFactory(parent=education_group_year, child_branch=child_mandatory)

        # Create another training
        another_training = TrainingFactory(academic_year=self.academic_year)
        GroupElementYearFactory(parent=another_training, child_branch=child_mandatory)

        delete.start(education_group_year)
        with self.assertRaises(EducationGroupYear.DoesNotExist):
            EducationGroupYear.objects.get(pk=education_group_year.pk)
        with self.assertRaises(GroupElementYear.DoesNotExist):
            GroupElementYear.objects.get(pk=link_parent_child.pk)

        self.assertEqual(
            child_mandatory,
            EducationGroupYear.objects.get(pk=child_mandatory.pk)
        )
