##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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

import program_management.business
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_types
from base.models.group_element_year import GroupElementYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory, TrainingFactory, GroupFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from program_management.business.group_element_years.group_element_year_tree import EducationGroupHierarchy


class TestPath(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(current=True)
        cls.root = EducationGroupYearFactory(academic_year=cls.academic_year)
        cls.group_element_year = GroupElementYearFactory(parent=cls.root, child_branch__academic_year=cls.academic_year)

    def test_path_of_root_is_equal_to_minus_1(self):
        node = EducationGroupHierarchy(self.root)
        self.assertEqual(
            node.path,
            "{}".format(self.root.id)
        )

    def test_path_of_child_is_equal_to_parent_path_plus_parent_id(self):
        node = EducationGroupHierarchy(self.root)
        child = node.children[0]
        self.assertEqual(
            child.path,
            "{}_{}".format(self.root.id, self.group_element_year.child_branch.id)
        )


class TestFetchGroupElementsBehindHierarchy(TestCase):
    """Unit tests on fetch_all_group_elements_behind_hierarchy()"""
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory()
        cls.root = TrainingFactory(
            acronym='DROI2M',
            education_group_type__name=education_group_types.TrainingType.PGRM_MASTER_120.name,
            academic_year=cls.academic_year
        )

        finality_list = GroupFactory(
            acronym='LIST FINALITIES',
            education_group_type__name=education_group_types.GroupType.FINALITY_120_LIST_CHOICE.name,
            academic_year=cls.academic_year
        )

        formation_master_md = TrainingFactory(
            acronym='DROI2MD',
            education_group_type__name=education_group_types.TrainingType.MASTER_MD_120.name,
            academic_year=cls.academic_year
        )

        common_core = GroupFactory(
            acronym='TC DROI2MD',
            education_group_type__name=education_group_types.GroupType.COMMON_CORE.name,
            academic_year=cls.academic_year
        )

        cls.link_1 = GroupElementYearFactory(parent=cls.root, child_branch=finality_list, child_leaf=None)
        cls.link_1_bis = GroupElementYearFactory(parent=cls.root,
                                                 child_branch=EducationGroupYearFactory(
                                                     academic_year=cls.academic_year),
                                                 child_leaf=None)
        cls.link_2 = GroupElementYearFactory(parent=finality_list, child_branch=formation_master_md, child_leaf=None)
        cls.link_3 = GroupElementYearFactory(parent=formation_master_md, child_branch=common_core, child_leaf=None)
        cls.link_4 = GroupElementYearFactory(parent=common_core,
                                             child_leaf=LearningUnitYearFactory(),
                                             child_branch=None)

    def test_with_one_root_id(self):
        queryset = GroupElementYear.objects.all().select_related(
            'child_branch__academic_year',
            'child_leaf__academic_year',
            # [...] other fetch
        )
        result = program_management.business.group_element_years.group_element_year_tree.fetch_all_group_elements_in_tree(self.root, queryset)
        expected_result = {
            self.link_1.parent_id: [self.link_1, self.link_1_bis],
            self.link_2.parent_id: [self.link_2],
            self.link_3.parent_id: [self.link_3],
            self.link_4.parent_id: [self.link_4],
        }
        self.assertDictEqual(result, expected_result)

    def test_when_queryset_is_not_from_group_element_year_model(self):
        wrong_queryset_model = EducationGroupYear.objects.all()
        with self.assertRaises(AttributeError):
            program_management.business.group_element_years.group_element_year_tree.fetch_all_group_elements_in_tree(self.root, wrong_queryset_model)