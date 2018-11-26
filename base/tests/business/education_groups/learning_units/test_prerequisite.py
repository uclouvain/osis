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
#############################################################################
import itertools

from django.test import TestCase

from base.business.education_groups.learning_units.prerequisite import extract_learning_units_acronym_from_prerequisite, \
    get_learning_units_which_are_outside_of_education_group
from base.models.enums.prerequisite_operator import AND, OR
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import TrainingFactory, MiniTrainingFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFakerFactory, LearningUnitYearFactory
from base.tests.factories.prerequisite import PrerequisiteFactory
from base.tests.factories.prerequisite_item import PrerequisiteItemFactory


class TestLearningUnitsAcronymsFromPrerequisite(TestCase):
    def setUp(self):
        self.prerequisite = PrerequisiteFactory()

    def test_empty_prerequisite_should_return_empty_list(self):
        self.assertEqual(extract_learning_units_acronym_from_prerequisite(self.prerequisite),
                         [])

    def test_when_prerequisite_consits_of_one_learning_unit(self):
        learning_unit_year = LearningUnitYearFactory(acronym="LSINF1121")
        PrerequisiteItemFactory(
            learning_unit=learning_unit_year.learning_unit,
            prerequisite=self.prerequisite
        )

        self.assertEqual(
            extract_learning_units_acronym_from_prerequisite(self.prerequisite),
            ["LSINF1121"]
        )

    def test_when_prerequisites_multiple_learning_units_but_no_parentheses(self):
        learning_unit_year = LearningUnitYearFactory(acronym="LSINF1121")
        PrerequisiteItemFactory(
            learning_unit=learning_unit_year.learning_unit,
            prerequisite=self.prerequisite,
            group_number=1,
            position=1,
        )
        learning_unit_year = LearningUnitYearFactory(acronym="LBIR1245A")
        PrerequisiteItemFactory(
            learning_unit=learning_unit_year.learning_unit,
            prerequisite=self.prerequisite,
            group_number=2,
            position=1,
        )
        learning_unit_year = LearningUnitYearFactory(acronym="LDROI4578")
        PrerequisiteItemFactory(
            learning_unit=learning_unit_year.learning_unit,
            prerequisite=self.prerequisite,
            group_number=3,
            position=1,
        )

        self.prerequisite.main_operator = AND
        self.prerequisite.save()
        self.assertCountEqual(
            extract_learning_units_acronym_from_prerequisite(self.prerequisite),
            ["LSINF1121", "LBIR1245A", "LDROI4578"]
        )

        self.prerequisite.main_operator = OR
        self.prerequisite.save()
        self.assertCountEqual(
            extract_learning_units_acronym_from_prerequisite(self.prerequisite),
            ["LSINF1121", "LBIR1245A", "LDROI4578"]
        )

    def test_when_prerequisites_multiple_learning_units_with_parentheses(self):
        learning_unit_year = LearningUnitYearFactory(acronym="LSINF1121")
        PrerequisiteItemFactory(
            learning_unit=learning_unit_year.learning_unit,
            prerequisite=self.prerequisite,
            group_number=1,
            position=1,
        )
        learning_unit_year = LearningUnitYearFactory(acronym="LBIR1245A")
        PrerequisiteItemFactory(
            learning_unit=learning_unit_year.learning_unit,
            prerequisite=self.prerequisite,
            group_number=1,
            position=2,
        )
        learning_unit_year = LearningUnitYearFactory(acronym="LDROI4578")
        PrerequisiteItemFactory(
            learning_unit=learning_unit_year.learning_unit,
            prerequisite=self.prerequisite,
            group_number=2,
            position=1,
        )

        self.prerequisite.main_operator = AND
        self.prerequisite.save()
        self.assertCountEqual(
            extract_learning_units_acronym_from_prerequisite(self.prerequisite),
            ["LSINF1121", "LBIR1245A", "LDROI4578"]
        )

        self.prerequisite.main_operator = OR
        self.prerequisite.save()
        self.assertCountEqual(
            extract_learning_units_acronym_from_prerequisite(self.prerequisite),
            ["LSINF1121", "LBIR1245A", "LDROI4578"]
        )


class TestGetLearningUnitsWhichAreNotInsideTraining(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory()
        cls.education_group_year_root = TrainingFactory(academic_year=cls.academic_year)
        cls.education_group_year_childs = [MiniTrainingFactory(academic_year=cls.academic_year) for _ in range(0,3)]

        cls.group_element_years_root_to_child = [
            GroupElementYearFactory(parent=cls.education_group_year_root,
                                    child_leaf=None,
                                    child_branch=cls.education_group_year_childs[i])
            for i in range(0, len(cls.education_group_year_childs))
        ]

        cls.group_element_years_child_0 = [
            GroupElementYearFactory(parent=cls.education_group_year_childs[0],
                                    child_leaf=LearningUnitYearFakerFactory(
                                        learning_container_year__academic_year=cls.academic_year),
                                    child_branch=None)
            for i in range(0, 2)
        ]

        cls.group_element_years_child_2 = [
            GroupElementYearFactory(parent=cls.education_group_year_childs[2],
                                    child_leaf=LearningUnitYearFakerFactory(
                                        learning_container_year__academic_year=cls.academic_year),
                                    child_branch=None)
            for i in range(0, 4)
        ]

        cls.all_learning_units_acronym = [
            gey.child_leaf.acronym for gey in itertools.chain(cls.group_element_years_child_0,
                                                              cls.group_element_years_child_2)
        ]

    def test_empty_acronym_list_should_return_empty_list(self):
        self.assertEqual(get_learning_units_which_are_outside_of_education_group(self.education_group_year_root, []),
                         [])

    def test_should_return_empty_list_when_all_learning_units_are_inside_education_group_year_root(self):
        self.assertEqual(get_learning_units_which_are_outside_of_education_group(self.education_group_year_root,
                                                                                 self.all_learning_units_acronym),
                         [])

    def test_should_return_acronym_of_learnings_units_not_present_in_education_group_year(self):
        luy_outside = LearningUnitYearFakerFactory(learning_container_year__academic_year=self.academic_year)
        luy_outside_2 = LearningUnitYearFakerFactory(learning_container_year__academic_year=self.academic_year)
        learning_units_acronym = [luy_outside.acronym] + self.all_learning_units_acronym
        self.assertEqual(get_learning_units_which_are_outside_of_education_group(self.education_group_year_root,
                                                                                 learning_units_acronym),
                         [luy_outside.acronym])

        learning_units_acronym = [luy_outside.acronym, luy_outside_2.acronym] + self.all_learning_units_acronym
        self.assertCountEqual(get_learning_units_which_are_outside_of_education_group(self.education_group_year_root,
                                                                                      learning_units_acronym),
                         [luy_outside.acronym, luy_outside_2.acronym])
