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

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.test import TestCase
from django.urls import reverse

from base.business.education_groups.group_element_year_tree import EducationGroupHierarchy
from base.models.enums.education_group_types import MiniTrainingType
from base.models.enums.link_type import LinkTypes
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory


class TestBuildTree(TestCase):
    def setUp(self):
        self.parent = EducationGroupYearFactory()
        self.group_element_year_1 = GroupElementYearFactory(
            parent=self.parent
        )
        self.group_element_year_1_1 = GroupElementYearFactory(
            parent=self.group_element_year_1.child_branch
        )
        self.group_element_year_2 = GroupElementYearFactory(
            parent=self.parent
        )
        self.group_element_year_2_1 = GroupElementYearFactory(
            parent=self.group_element_year_2.child_branch,
            child_branch=None,
            child_leaf=LearningUnitYearFactory()
        )

    def test_init_tree(self):
        node = EducationGroupHierarchy(self.parent)

        self.assertEqual(node.education_group_year, self.parent)
        self.assertEqual(len(node.children), 2)
        self.assertEqual(node.children[0].group_element_year, self.group_element_year_1)
        self.assertEqual(node.children[1].group_element_year, self.group_element_year_2)

        self.assertEqual(node.children[0].children[0].group_element_year, self.group_element_year_1_1)
        self.assertEqual(node.children[1].children[0].group_element_year, self.group_element_year_2_1)

        self.assertEqual(node.children[0].children[0].education_group_year, self.group_element_year_1_1.child_branch)
        self.assertEqual(node.children[1].children[0].education_group_year, None)
        self.assertEqual(node.children[1].children[0].learning_unit_year, self.group_element_year_2_1.child_leaf)

    def test_tree_to_json(self):
        node = EducationGroupHierarchy(self.parent)

        json = node.to_json()
        self.assertEqual(json['text'], self.parent.verbose)

        self.assertEqual(json['a_attr']['href'], reverse('education_group_read', args=[
            self.parent.pk, self.parent.pk]) + "?group_to_parent=0")

        self.assertEqual(
            json['children'][1]['children'][0]['a_attr']['href'],
            reverse(
                'learning_unit_utilization',
                args=[self.parent.pk, self.group_element_year_2_1.child_leaf.pk]
            ) + "?group_to_parent={}".format(self.group_element_year_2_1.pk))

    def test_tree_to_json_ids(self):
        node = EducationGroupHierarchy(self.parent)
        json = node.to_json()

        self.assertEquals(
            json['children'][1]['id'],
            "id_{}_{}".format(
                node.children[1].education_group_year.pk,
                node.children[1].group_element_year.pk if node.children[1].group_element_year else '#'
            )
        )

        self.assertEquals(
            json['children'][1]['children'][0]['id'],
            "id_{}_{}".format(
                node.children[1].children[0].learning_unit_year.pk,
                node.children[1].children[0].group_element_year.pk if node.children[1].group_element_year else '#'
            )
        )

    def test_build_tree_reference(self):
        """
        This tree contains a reference link.
        """
        self.group_element_year_1.link_type = LinkTypes.REFERENCE.name
        self.group_element_year_1.save()

        node = EducationGroupHierarchy(self.parent)

        self.assertEqual(node.children[0]._get_icon(),  static('img/reference.jpg'))

        list_children = node.to_list()
        self.assertEqual(list_children, [
            self.group_element_year_1_1,
            self.group_element_year_2, [self.group_element_year_2_1]
        ])

    def test_node_to_list_flat(self):
        node = EducationGroupHierarchy(self.parent)
        list_children = node.to_list(flat=True)

        self.assertCountEqual(list_children, [
            self.group_element_year_1,
            self.group_element_year_1_1,
            self.group_element_year_2,
            self.group_element_year_2_1
        ])

    def test_node_to_list_without_reference_content(self):
        """
        This test ensure that if the parameter with_reference_content is specified to False,
        all content related to reference linked is not returned
        """
        self.group_element_year_1.link_type = LinkTypes.REFERENCE.name
        self.group_element_year_1.save()

        node = EducationGroupHierarchy(self.parent)
        list_children = node.to_list(with_reference_content=False, flat=True)

        self.assertCountEqual(list_children, [
            self.group_element_year_2,
            self.group_element_year_2_1
        ])


class TestGetOptionList(TestCase):
    def setUp(self):
        self.academic_year = AcademicYearFactory(current=True)
        self.root = EducationGroupYearFactory(academic_year=self.academic_year)

    def test_get_option_list_case_no_result(self):
        node = EducationGroupHierarchy(self.root)
        self.assertListEqual(node.get_option_list(), [])

    def test_get_option_list_case_result_found(self):
        option_1 = EducationGroupYearFactory(
            academic_year=self.academic_year,
            education_group_type__name=MiniTrainingType.OPTION.name
        )
        GroupElementYearFactory(parent=self.root, child_branch=option_1)
        node = EducationGroupHierarchy(self.root)

        self.assertListEqual(node.get_option_list(), [option_1])

    def test_get_option_list_case_multiple_result_found_on_different_children(self):
        list_option = []
        for _ in range(5):
            egy_child = EducationGroupYearFactory(academic_year=self.academic_year)
            GroupElementYearFactory(parent=self.root, child_branch=egy_child)

            option = EducationGroupYearFactory(
                academic_year=self.academic_year,
                education_group_type__name=MiniTrainingType.OPTION.name
            )
            list_option.append(option)
            GroupElementYearFactory(parent=egy_child, child_branch=option)

        node = EducationGroupHierarchy(self.root)
        self.assertCountEqual(node.get_option_list(), list_option)
