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
from unittest.mock import patch

from django.test import TestCase

from base.models.enums.education_group_types import TrainingType
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.campus import CampusFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory, TrainingEducationGroupTypeFactory
from base.tests.factories.entity_version import EntityVersionFactory
from education_group.models.group import Group
from education_group.models.group_year import GroupYear
from program_management.ddd.domain.node import Node
from program_management.ddd.repositories.program_tree import ProgramTreeRepository
from program_management.models.element import Element
from program_management.tests.ddd.factories.node import NodeIdentityFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory, ProgramTreeIdentityFactory


class TestProgramTreeRepositoryCreateMethod(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.year = AcademicYearFactory(current=True).year
        cls.entity_identity = ProgramTreeIdentityFactory(year=cls.year)
        cls.node_identity = NodeIdentityFactory(year=cls.year, code=cls.entity_identity.code)
        cls.education_group_type_model_obj = TrainingEducationGroupTypeFactory()
        cls.campus_model_obj = CampusFactory()
        cls.entity_version_model_obj = EntityVersionFactory()

        cls.repository = ProgramTreeRepository()

    @patch.object(Node, '_has_changed', return_value=True)
    def test_creates_node_if_not_exists(self, *mocks):
        new_program_tree = ProgramTreeFactory(
            root_node__year=self.node_identity.year,
            root_node__code=self.node_identity.code,
            root_node__start_year=self.year,
            root_node__end_date=self.year,
            root_node__node_type=TrainingType[self.education_group_type_model_obj.name],
            root_node__teaching_campus=self.campus_model_obj.name,
            root_node__management_entity_acronym=self.entity_version_model_obj.acronym,
        )

        self.repository.create(new_program_tree)

        group_db_object = Group.objects.get(
            groupyear__partial_acronym=new_program_tree.root_node.code,
            groupyear__academic_year__year=new_program_tree.root_node.year,
        )

        group_year_db_object = GroupYear.objects.get(
            partial_acronym=new_program_tree.root_node.code,
            academic_year__year=new_program_tree.root_node.year,
        )

        element_db_object = Element.objects.get(group_year=group_year_db_object)

        # Group Model field mapping assertions
        self.assertEqual(group_db_object.start_year.year, new_program_tree.root_node.start_year)
        self.assertEqual(group_db_object.end_year.year, new_program_tree.root_node.end_date)
        self.assertIsNone(group_db_object.external_id)

        # GroupYear Model field mapping assertions
        self.assertEqual(group_year_db_object.group, group_db_object)
        self.assertEqual(group_year_db_object.partial_acronym, new_program_tree.root_node.code)
        self.assertEqual(group_year_db_object.academic_year.year, new_program_tree.root_node.year)
        self.assertEqual(group_year_db_object.education_group_type.name, new_program_tree.root_node.node_type.name)
        self.assertEqual(group_year_db_object.credits, new_program_tree.root_node.credits)
        self.assertEqual(group_year_db_object.constraint_type, new_program_tree.root_node.constraint_type)
        self.assertEqual(group_year_db_object.min_constraint, new_program_tree.root_node.min_constraint)
        self.assertEqual(group_year_db_object.max_constraint, new_program_tree.root_node.max_constraint)
        self.assertEqual(group_year_db_object.title_fr, new_program_tree.root_node.group_title_fr)
        self.assertEqual(group_year_db_object.title_en, new_program_tree.root_node.group_title_en)
        self.assertEqual(group_year_db_object.remark_fr, new_program_tree.root_node.remark_fr)
        self.assertEqual(group_year_db_object.remark_en, new_program_tree.root_node.remark_en)
        self.assertEqual(group_year_db_object.management_entity.most_recent_acronym, new_program_tree.root_node.management_entity_acronym)
        self.assertEqual(group_year_db_object.main_teaching_campus.name, new_program_tree.root_node.teaching_campus)

        # Element Model field mapping assertions
        self.assertEqual(element_db_object.group_year, group_year_db_object)
        self.assertIsNone(element_db_object.learning_unit_year)
        self.assertIsNone(element_db_object.learning_class_year)
