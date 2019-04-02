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
from unittest import mock

from django.core.exceptions import ValidationError
from django.test import TestCase

from base.business.group_element_years.detach import DetachEducationGroupYearStrategy
from base.models.enums.education_group_types import TrainingType, GroupType, MiniTrainingType
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import TrainingFactory, GroupFactory, MiniTrainingFactory
from base.tests.factories.group_element_year import GroupElementYearFactory


class TestOptionDetachEducationGroupYearStrategy(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory()
        cls.master_120 = TrainingFactory(education_group_type__name=TrainingType.PGRM_MASTER_120.name,
                                         academic_year=cls.academic_year)

        cls.option_in_parent = MiniTrainingFactory(
            acronym="OPT1",
            education_group_type__name=MiniTrainingType.OPTION.name,
            academic_year=cls.academic_year
        )
        cls.master_120_link_option = GroupElementYearFactory(parent=cls.master_120, child_branch=cls.option_in_parent)

        # Create finality structure
        cls.finality_group = GroupFactory(education_group_type__name=GroupType.FINALITY_120_LIST_CHOICE.name,
                                          academic_year=cls.academic_year)
        GroupElementYearFactory(parent=cls.master_120, child_branch=cls.finality_group)

        cls.master_120_specialized = GroupFactory(education_group_type__name=TrainingType.MASTER_MS_120.name,
                                                  academic_year=cls.academic_year)
        GroupElementYearFactory(parent=cls.finality_group, child_branch=cls.master_120_specialized)

    def setUp(self):
        self.authorized_relationship_patcher = mock.patch(
            "base.business.group_element_years.management.check_authorized_relationship",
            return_value=True
        )
        self.mocked_perm = self.authorized_relationship_patcher.start()
        self.addCleanup(self.authorized_relationship_patcher.stop)

    def test_is_valid_case_detach_option_which_are_not_within_finality_master_120(self):
        """
        In this test, we ensure that we can detach an option at 2m because it is not present in any finality 2m
        """
        strategy = DetachEducationGroupYearStrategy(link=self.master_120_link_option)
        self.assertTrue(strategy.is_valid())

    def test_is_valid_case_detach_groups_which_contains_options_which_are_not_within_master_120(self):
        """
        In this test, we ensure that we can detach a groups which contains options at 2m because
        this options are present in any finality of this 2m
        """
        subgroup = GroupFactory(education_group_type__name=GroupType.SUB_GROUP.name,
                                academic_year=self.academic_year)
        master_120_link_subgroup = GroupElementYearFactory(parent=self.master_120, child_branch=subgroup)
        GroupElementYearFactory(parent=subgroup, child_branch=self.option_in_parent)

        strategy = DetachEducationGroupYearStrategy(link=master_120_link_subgroup)
        self.assertTrue(strategy.is_valid())

    def test_is_valid_case_detach_option_which_are_within_finality_master_120_but_present_more_time_in_2m(self):
        """
        In this test, we ensure that we can detach an option at 2m level because it is present two time in 2m and
        it is present in one finality of this 2m but, we will detach only one link in 2m
        """
        subgroup = GroupFactory(education_group_type__name=GroupType.SUB_GROUP.name,
                                academic_year=self.academic_year)
        master_120_link_subgroup = GroupElementYearFactory(parent=self.master_120, child_branch=subgroup)
        GroupElementYearFactory(parent=subgroup, child_branch=self.option_in_parent)

        GroupElementYearFactory(parent=self.master_120_specialized, child_branch=self.option_in_parent)
        strategy = DetachEducationGroupYearStrategy(link=master_120_link_subgroup)
        self.assertTrue(strategy.is_valid())

    def test_is_not_valid_case_detach_option_which_are_within_finality_master_120(self):
        """
        In this test, we ensure that we CANNOT detach an option at 2m level because
        it is present in one finality of this 2m
        """
        option = MiniTrainingFactory(education_group_type__name=MiniTrainingType.OPTION.name,
                                     academic_year=self.academic_year)
        GroupElementYearFactory(parent=self.master_120_specialized, child_branch=option)
        master_120_link_option = GroupElementYearFactory(
            parent=self.master_120,
            child_branch=option,
        )

        strategy = DetachEducationGroupYearStrategy(link=master_120_link_option)
        with self.assertRaises(ValidationError):
            strategy.is_valid()

    def test_is_not_valid_case_detach_group_which_contains_option_which_are_within_finality_master_120(self):
        """
        In this test, we ensure that we CANNOT detach a group which contains options at 2m level because
        this options are present in one finality of this 2m
        """
        subgroup = GroupFactory(education_group_type__name=GroupType.SUB_GROUP.name,
                                academic_year=self.academic_year)
        GroupElementYearFactory(parent=self.master_120_specialized, child_branch=subgroup)
        option = MiniTrainingFactory(education_group_type__name=MiniTrainingType.OPTION.name,
                                     academic_year=self.academic_year)
        GroupElementYearFactory(parent=subgroup, child_branch=option)

        master_120_link_option = GroupElementYearFactory(parent=self.master_120, child_branch=option)

        strategy = DetachEducationGroupYearStrategy(link=master_120_link_option)
        with self.assertRaises(ValidationError):
            strategy.is_valid()

    def test_is_not_valid_case_detach_group_which_contains_option_which_are_reused_in_multiple_2M(self):
        """
        In this test, we ensure that we CANNOT detach a group which are reused in two 2m because, one of
        those 2m structure will not be valid anymore
        """
        # Create first 2M
        #   2M
        #   |--OPT1
        #   |--GROUP1
        #      |--OPT1
        #   |--FINALITY_LIST
        #      |--2MS
        #         |--OPT1
        subgroup = GroupFactory(acronym='GROUP1', education_group_type__name=GroupType.SUB_GROUP.name,
                                academic_year=self.academic_year)
        GroupElementYearFactory(parent=self.master_120, child_branch=subgroup)
        group1_link_opt1 = GroupElementYearFactory(parent=subgroup, child_branch=self.option_in_parent)
        GroupElementYearFactory(parent=self.master_120_specialized, child_branch=self.option_in_parent)

        # Create another 2M
        #   2M
        #   |--GROUP1
        #      |--OPT1
        #   |--FINALITY_LIST
        #      |--2MD
        #         |--OPT1
        another_master_120 = TrainingFactory(education_group_type__name=TrainingType.PGRM_MASTER_120.name,
                                             academic_year=self.academic_year)
        GroupElementYearFactory(parent=another_master_120, child_branch=subgroup)
        another_finality_group = GroupFactory(education_group_type__name=GroupType.FINALITY_120_LIST_CHOICE.name,
                                              academic_year=self.academic_year)
        GroupElementYearFactory(parent=another_master_120, child_branch=another_finality_group)
        another_master_120_didactic = GroupFactory(education_group_type__name=TrainingType.MASTER_MD_120.name,
                                                   academic_year=self.academic_year)
        GroupElementYearFactory(parent=another_finality_group, child_branch=another_master_120_didactic)
        GroupElementYearFactory(parent=another_master_120_didactic, child_branch=self.option_in_parent)

        # We try to detach OPT1 from GROUP1 but it is not allowed because another 2M structure won't be valid anymore
        strategy = DetachEducationGroupYearStrategy(link=group1_link_opt1)
        with self.assertRaises(ValidationError):
            strategy.is_valid()
