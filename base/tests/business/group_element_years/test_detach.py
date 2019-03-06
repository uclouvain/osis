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
from django.core.exceptions import ValidationError
from django.test import TestCase

from base.business.group_element_years.detach import DetachEducationGroupYearStrategy
from base.models.enums.education_group_types import TrainingType, GroupType, MiniTrainingType
from base.tests.factories.education_group_year import TrainingFactory, GroupFactory, MiniTrainingFactory
from base.tests.factories.group_element_year import GroupElementYearFactory


class TestDetachEducationGroupYearStrategy(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.master_120 = TrainingFactory(education_group_type__name=TrainingType.PGRM_MASTER_120.name)

        cls.option_in_parent = MiniTrainingFactory(education_group_type__name=MiniTrainingType.OPTION.name)
        cls.master_120_link_option = GroupElementYearFactory(parent=cls.master_120, child_branch=cls.option_in_parent)

        # Create finality structure
        cls.finality_group = GroupFactory(education_group_type__name=GroupType.FINALITY_120_LIST_CHOICE.name)
        GroupElementYearFactory(parent=cls.master_120, child_branch=cls.finality_group)

        cls.master_120_specialized = GroupFactory(education_group_type__name=TrainingType.MASTER_MS_120.name)
        GroupElementYearFactory(parent=cls.finality_group, child_branch=cls.master_120_specialized)

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
        subgroup = GroupFactory(education_group_type__name=GroupType.SUB_GROUP.name)
        master_120_link_subgroup = GroupElementYearFactory(parent=self.master_120, child_branch=subgroup)
        GroupElementYearFactory(parent=subgroup, child_branch=self.option_in_parent)

        strategy = DetachEducationGroupYearStrategy(link=master_120_link_subgroup)
        self.assertTrue(strategy.is_valid())

    def test_is_not_valid_case_detach_option_which_are_within_finality_master_120(self):
        """
        In this test, we ensure that we CANNOT detach an option at 2m level because
        it is present in one finality of this 2m
        """
        option = MiniTrainingFactory(education_group_type__name=MiniTrainingType.OPTION.name)
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
        this options are not present in one finality of this 2m
        """
        subgroup = GroupFactory(education_group_type__name=GroupType.SUB_GROUP.name)
        GroupElementYearFactory(parent=self.master_120_specialized, child_branch=subgroup)
        option = MiniTrainingFactory(education_group_type__name=MiniTrainingType.OPTION.name)
        GroupElementYearFactory(parent=subgroup, child_branch=option)

        master_120_link_option = GroupElementYearFactory(parent=self.master_120, child_branch=option)

        strategy = DetachEducationGroupYearStrategy(link=master_120_link_option)
        with self.assertRaises(ValidationError):
            strategy.is_valid()
