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
from django.utils.translation import ugettext_lazy as _

from base.business.education_groups.create import create_child
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_types, education_group_categories
from base.tests.factories.authorized_relationship import AuthorizedRelationshipFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.validation_rule import ValidationRuleFactory


class CreateChild(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.master_type = EducationGroupTypeFactory(
            category=education_group_categories.TRAINING,
            name=education_group_types.TrainingType.MASTER_MA_120.name,
        )
        cls.finality_type = EducationGroupTypeFactory(
            category=education_group_categories.GROUP,
            name=education_group_types.GroupType.FINALITY_120_LIST_CHOICE.name,
        )
        cls.egy = EducationGroupYearFactory(
            education_group_type=cls.master_type,
            acronym="TEST2M",
            partial_acronym="LTEST100B",
        )

    def setUp(self):
        self.auth_rel = AuthorizedRelationshipFactory(
            parent_type=self.master_type,
            child_type=self.finality_type,
        )
        self.validation_rule_title = ValidationRuleFactory(
            field_reference="base.validationrule,base_educationgroupyear.title"
                            ".osis.education_group_type_finality120listchoice",
            initial_value="Liste au choix de Finalités",
        )
        self.validation_rule_partial_acronym = ValidationRuleFactory(
            field_reference="base_educationgroupyear.partial_acronym.osis.education_group_type_finality120listchoice",
            initial_value="400G",
        )

    def test_should_inherit_attributes_from_parent_egy(self):
        attributes_to_inherit = ("academic_year", "main_teaching_campus", "management_entity")
        child_egy = create_child(self.egy, self.finality_type, self.validation_rule_title,
                                 self.validation_rule_partial_acronym)

        self.assertIsInstance(child_egy, EducationGroupYear)
        self.assert_fields_equal(
            self.egy,
            child_egy,
            attributes_to_inherit
        )

    def test_should_have_education_group_type_equal_to_argument(self):
        child_egy = create_child(self.egy, self.finality_type, self.validation_rule_title,
                                 self.validation_rule_partial_acronym)
        self.assertEqual(
            child_egy.education_group_type,
            self.finality_type
        )

    def test_should_have_title_equal_to_initial_value_of_validation_rule(self):
        child_egy = create_child(self.egy, self.finality_type, self.validation_rule_title,
                                 self.validation_rule_partial_acronym)
        self.assertEqual(
            child_egy.title,
            self.validation_rule_title.initial_value
        )

    def test_should_format_the_partial_acronym_based_on_parent_and_validation_rule(self):
        child_egy = create_child(self.egy, self.finality_type, self.validation_rule_title,
                                 self.validation_rule_partial_acronym)
        self.assertEqual(
            child_egy.partial_acronym,
            "LTEST400G"
        )

    def test_should_increment_cnum_of_child_partial_acronym_to_avoid_conflicted_acronyms(self):
        EducationGroupYearFactory(partial_acronym="LTEST400G")
        EducationGroupYearFactory(partial_acronym="LTEST401G")
        child_egy = create_child(self.egy, self.finality_type, self.validation_rule_title,
                                 self.validation_rule_partial_acronym)
        self.assertEqual(
            child_egy.partial_acronym,
            "LTEST402G"
        )

    def test_should_format_acronym_based_on_education_group_type_and_parent_acronym(self):
        child_egy = create_child(self.egy, self.finality_type, self.validation_rule_title,
                                 self.validation_rule_partial_acronym)
        expected_acronym = "{}{}".format(
            self.validation_rule_title.initial_value.replace(" ", "").upper(),
            self.egy.acronym
        )

        self.assertEqual(
            child_egy.acronym,
            expected_acronym
        )

    def test_should_create_education_group_with_start_and_year_equal_to_parent_academic_year(self):
        child_egy = create_child(self.egy, self.finality_type, self.validation_rule_title,
                                 self.validation_rule_partial_acronym)
        self.assertEqual(
            child_egy.education_group.start_year,
            self.egy.academic_year.year
        )
        self.assertEqual(
            child_egy.education_group.end_year,
            self.egy.academic_year.year
        )

    def test_should_save_child(self):
        child_egy = create_child(self.egy, self.finality_type, self.validation_rule_title,
                                 self.validation_rule_partial_acronym)
        self.assertTrue(child_egy.id)

    def assert_fields_equal(self, obj1, obj2, fields):
        for field in fields:
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(obj1, field),
                    getattr(obj2, field)
                )
