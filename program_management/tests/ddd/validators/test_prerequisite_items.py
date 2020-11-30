# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from django.test import SimpleTestCase

from base.models.enums.education_group_types import TrainingType, MiniTrainingType
from program_management.ddd.validators._prerequisites_items import PrerequisiteItemsValidator
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeLearningUnitYearFactory, NodeGroupYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory


class TestPrerequisiteItemsValidator(SimpleTestCase):
    def setUp(self):
        self.program_tree = ProgramTreeFactory()
        LinkFactory(
            parent=self.program_tree.root_node,
            child=NodeLearningUnitYearFactory(code="LOSIS1121")
        )
        LinkFactory(
            parent=self.program_tree.root_node,
            child=NodeLearningUnitYearFactory(code="MARC2547")
        )
        LinkFactory(
            parent=self.program_tree.root_node,
            child=NodeLearningUnitYearFactory(code="MECK8960")
        )
        LinkFactory(
            parent=self.program_tree.root_node,
            child=NodeLearningUnitYearFactory(code="BREM5890")
        )

    def test_should_be_valid_when_empty_prerequisite_string(self):
        prerequisite_string = ""
        node = NodeLearningUnitYearFactory()
        self.assertTrue(
            PrerequisiteItemsValidator(prerequisite_string, node, self.program_tree).is_valid()
        )

    def test_should_be_invalid_when_codes_used_in_prerequisite_are_not_present_in_program_tree(self):
        prerequisite_string = "LOSIS1121 ET MARC2589"
        node = NodeLearningUnitYearFactory()
        self.assertFalse(
            PrerequisiteItemsValidator(prerequisite_string, node, self.program_tree).is_valid()
        )

    def test_should_be_invalid_when_codes_used_in_prerequisite_string_is_node_code(self):
        prerequisite_string = "LOSIS1121 ET MARC2547"
        node = NodeLearningUnitYearFactory(code="LOSIS1121")
        self.assertFalse(
            PrerequisiteItemsValidator(prerequisite_string, node, self.program_tree).is_valid()
        )

    def test_should_be_valid_when_codes_used_in_prerequisite_string_are_permitted(self):
        prerequisite_string = "LOSIS1121 ET MARC2547 ET (BREM5890 OU MECK8960)"
        node = NodeLearningUnitYearFactory()
        self.assertTrue(
            PrerequisiteItemsValidator(prerequisite_string, node, self.program_tree).is_valid()
        )

    def test_should_be_invalid_when_codes_used_in_minor_or_deepening(self):
        minor_or_deepening_types = (
            MiniTrainingType.OPEN_MINOR,
            MiniTrainingType.ACCESS_MINOR,
            MiniTrainingType.DISCIPLINARY_COMPLEMENT_MINOR,
            MiniTrainingType.SOCIETY_MINOR,
            MiniTrainingType.DEEPENING,
        )
        for mini_training_type in minor_or_deepening_types:
            with self.subTest(mini_training_type=mini_training_type):
                program_tree = ProgramTreeFactory(root_node__node_type=TrainingType.BACHELOR)
                minor = NodeGroupYearFactory(node_id=9999, node_type=mini_training_type)
                ue = NodeLearningUnitYearFactory()
                LinkFactory(
                    parent=self.program_tree.root_node,
                    child=ue
                )
                LinkFactory(
                    parent=program_tree.root_node,
                    child=minor
                )
                code_not_permitted = "LOSIS9999"
                LinkFactory(
                    parent=minor,
                    child=NodeLearningUnitYearFactory(code=code_not_permitted)
                )
                prerequisite_string = code_not_permitted
                self.assertFalse(
                    PrerequisiteItemsValidator(prerequisite_string, ue, program_tree).is_valid()
                )
