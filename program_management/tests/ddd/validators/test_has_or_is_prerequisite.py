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
import copy
from unittest import mock

from django.test import SimpleTestCase

from base.models.enums.education_group_types import TrainingType, GroupType
from program_management.ddd.domain.exception import CannotDetachLearningUnitsWhoArePrerequisiteException, \
    CannotDetachLearningUnitsWhoHavePrerequisiteException
from program_management.ddd.repositories.program_tree import ProgramTreeRepository
from program_management.ddd.validators._has_or_is_prerequisite import _IsPrerequisiteValidator, \
    _HasPrerequisiteValidator, IsHasPrerequisiteForAllTreesValidator
from program_management.tests.ddd.factories.domain.prerequisite.prerequisite import PrerequisitesFactory
from program_management.tests.ddd.factories.domain.program_tree.LDROI200M_DROI2M import ProgramTreeDROI2MFactory
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeLearningUnitYearFactory, NodeGroupYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.validators.mixins import TestValidatorValidateMixin


class TestIsPrerequisiteValidator(TestValidatorValidateMixin, SimpleTestCase):

    def setUp(self):
        self.year = 2020
        self.tree = ProgramTreeDROI2MFactory(root_node__year=self.year)
        self.ldrop2011 = self.tree.get_node_by_code_and_year(code="LDROP2011", year=self.year)
        self.ldroi2101 = self.tree.get_node_by_code_and_year(code="LDROI2101", year=self.year)
        self.ldrop100t = self.tree.get_node_by_code_and_year(code="LDROP100T", year=self.year)
        self.ldroi220t = self.tree.get_node_by_code_and_year(code="LDROI220T", year=self.year)

    def test_should_not_raise_exception_when_children_of_node_to_detach_are_not_prerequisites(self):
        tree = copy.deepcopy(self.tree)
        node_without_prerequisite = self.tree.get_node_by_code_and_year(code="LDROP2013", year=self.year)
        validator = _IsPrerequisiteValidator(tree, node_to_detach=node_without_prerequisite)
        self.assertValidatorNotRaises(validator)

    def test_should_raise_exception_when_children_of_node_to_detach_are_prerequisites(self):
        tree = copy.deepcopy(self.tree)
        tree.set_prerequisite(
            prerequisite_expression="LDROI2101",
            node_having_prerequisites=self.ldrop2011
        )

        node_containing_child_that_is_prerequisite = self.ldroi220t

        with self.assertRaises(CannotDetachLearningUnitsWhoArePrerequisiteException):
            _IsPrerequisiteValidator(tree, node_to_detach=node_containing_child_that_is_prerequisite).validate()

    def test_should_raise_exception_when_node_to_detach_is_prerequisite(self):
        tree = copy.deepcopy(self.tree)
        tree.set_prerequisite(
            prerequisite_expression="LDROI2101",
            node_having_prerequisites=self.ldrop2011
        )

        node_that_is_prerequisite = self.ldroi2101

        with self.assertRaises(CannotDetachLearningUnitsWhoArePrerequisiteException):
            _IsPrerequisiteValidator(tree, node_to_detach=node_that_is_prerequisite).validate()

    def test_should_not_raise_exception_when_node_to_detach_is_prerequisite_twice(self):
        tree = ProgramTreeDROI2MFactory(root_node__year=self.year)
        ldrop2011 = tree.get_node_by_code_and_year(code="LDROP2011", year=self.year)
        ldroi2101 = tree.get_node_by_code_and_year(code="LDROI2101", year=self.year)
        ldrop100t = tree.get_node_by_code_and_year(code="LDROP100T", year=self.year)
        LinkFactory(
            parent=ldrop100t,
            child=ldroi2101  # learning unit used twice
        )

        tree.set_prerequisite(
            prerequisite_expression="LDROI2101",
            node_having_prerequisites=ldrop2011
        )
        node_that_is_prerequisite_and_used_twice_in_tree = ldroi2101
        self.assertTrue(tree.count_usage(node_that_is_prerequisite_and_used_twice_in_tree) == 2)

        assertion = "While the prerequisite is used more than once in the same tree, we can detach it"
        self.assertValidatorNotRaises(
            _IsPrerequisiteValidator(tree, node_to_detach=node_that_is_prerequisite_and_used_twice_in_tree)
        )

    @mock.patch.object(IsHasPrerequisiteForAllTreesValidator, 'search_trees_reusing_node')
    @mock.patch.object(IsHasPrerequisiteForAllTreesValidator, 'search_trees_inside_node')
    def test_should_not_raise_when_node_to_detach_has_prerequisite_and_is_program_tree(
            self,
            mock_trees_inside_node,
            mock_trees_reusing_node
    ):
        tree = copy.deepcopy(self.tree)

        mini_training_node = tree.get_node_by_code_and_year(code="LDROP221O", year=self.year)
        mini_training_tree = ProgramTreeFactory(root_node=mini_training_node)
        PrerequisitesFactory.produce_inside_tree(
            context_tree=mini_training_tree,
            node_having_prerequisite=self.ldrop2011.entity_id,
            nodes_that_are_prequisites=[tree.get_node_by_code_and_year(code="LDROP2012", year=self.year)]
        )

        mock_trees_inside_node.return_value = [mini_training_tree]
        mock_trees_reusing_node.return_value = [tree]

        assertion = """
            The node to detach is a minitraining where there are prerequisite only inside itself.
            In this case, we can detach it becauses prerequisites are not pertinent in the cotnext of the DROI2M.
        """
        self.assertValidatorNotRaises(
            IsHasPrerequisiteForAllTreesValidator(
                tree,
                node_to_detach=mini_training_node,
                parent_node=tree.get_node_by_code_and_year(code="LDROI100G", year=self.year),
                program_tree_repository=ProgramTreeRepository()
            )
        )


class TestHasPrerequisiteValidator(TestValidatorValidateMixin, SimpleTestCase):

    def setUp(self):
        self.year = 2020
        self.tree_droi2m = ProgramTreeDROI2MFactory(root_node__year=self.year)
        self.node_is_prerequisite = self.tree_droi2m.get_node_by_code_and_year(code="LDROI2101", year=self.year)
        self.node_has_prerequisite = self.tree_droi2m.get_node_by_code_and_year(code="LDROP2011", year=self.year)
        PrerequisitesFactory.produce_inside_tree(
            context_tree=self.tree_droi2m,
            node_having_prerequisite=self.node_has_prerequisite.entity_id,
            nodes_that_are_prequisites=[self.node_is_prerequisite.entity_id]
        )

    def test_should_not_raise_exception_when_children_of_node_to_detach_do_not_have_prerequisites(self):
        inexisting_node_in_tree = NodeGroupYearFactory()

        validator = _HasPrerequisiteValidator(self.tree_droi2m, node_to_detach=inexisting_node_in_tree)
        self.assertValidatorNotRaises(validator)

    def test_should_raise_exception_when_children_of_node_to_detach_have_prerequisites(self):
        parent_of_node_that_has_prerequisite = self.tree_droi2m.get_node_by_code_and_year(
            code="LDROP100T",
            year=self.year
        )

        with self.assertRaises(CannotDetachLearningUnitsWhoHavePrerequisiteException):
            _HasPrerequisiteValidator(self.tree_droi2m, node_to_detach=parent_of_node_that_has_prerequisite).validate()

    def test_should_raise_exception_when_node_to_detach_is_learning_unit_that_has_prerequisite(self):
        node_having_prerequisite = self.node_has_prerequisite

        with self.assertRaises(CannotDetachLearningUnitsWhoHavePrerequisiteException):
            _HasPrerequisiteValidator(self.tree_droi2m, node_to_detach=node_having_prerequisite).validate()

    def test_should_not_raise_exception_when_node_to_detach_has_prerequisite_twice(self):
        tree = ProgramTreeFactory()
        LinkFactory(
            parent=tree.root_node,
            child=self.node_is_prerequisite,
        )
        LinkFactory(
            parent=tree.root_node,
            child=LinkFactory(
                child=self.node_has_prerequisite
            ).parent
        )  # node_has_prerequisite used once
        LinkFactory(
            parent=tree.root_node,
            child=LinkFactory(
                child=self.node_has_prerequisite
            ).parent
        )  # node_has_prerequisite used twice

        assertion = "While the prerequisite is used more than once in the same tree, we can detach it"
        self.assertValidatorNotRaises(_HasPrerequisiteValidator(tree, node_to_detach=self.node_has_prerequisite))
