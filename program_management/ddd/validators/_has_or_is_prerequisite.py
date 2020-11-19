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
from typing import Set

from base.ddd.utils import business_validator
from program_management.ddd.business_types import *
from program_management.ddd.domain.exception import CannotDetachLearningUnitsWhoArePrerequisiteException, \
    CannotDetachLearningUnitsWhoHavePrerequisiteException


class IsHasPrerequisiteForAllTreesValidator(business_validator.BusinessValidator):
    def __init__(self, parent_node: 'Node', node_to_detach: 'Node', program_tree_repository: 'ProgramTreeRepository'):
        super().__init__()
        self.node_to_detach = node_to_detach
        self.parent_node = parent_node
        self.program_tree_repository = program_tree_repository

    def validate(self, *args, **kwargs):
        trees = self.program_tree_repository.search_from_children([self.parent_node.entity_id])
        for tree in trees:
            node_to_detach = tree.get_node_by_code_and_year(self.node_to_detach.code, self.node_to_detach.year)

            _IsPrerequisiteValidator(tree, node_to_detach).validate()
            _HasPrerequisiteValidator(tree, node_to_detach).validate()


class _IsPrerequisiteValidator(business_validator.BusinessValidator):

    def __init__(self, tree: 'ProgramTree', node_to_detach: 'Node'):
        super().__init__()
        self.node_to_detach = node_to_detach
        self.tree = tree

    def validate(self):
        nodes_that_are_prerequisites = self._get_nodes_that_are_prerequisite()
        if nodes_that_are_prerequisites:
            raise CannotDetachLearningUnitsWhoArePrerequisiteException(
                self.tree.root_node,
                nodes_that_are_prerequisites
            )

    def _get_nodes_that_are_prerequisite(self) -> Set['NodeLearningUnitYear']:
        learning_unit_nodes_detached = self.node_to_detach.get_all_children_as_learning_unit_nodes()
        if self.node_to_detach.is_learning_unit():
            learning_unit_nodes_detached.append(self.node_to_detach)

        return {n for n in learning_unit_nodes_detached if n.is_prerequisite}


class _HasPrerequisiteValidator(business_validator.BusinessValidator):

    def __init__(self, tree: 'ProgramTree', node_to_detach: 'Node'):
        super().__init__()
        self.node_to_detach = node_to_detach
        self.tree = tree

    def validate(self):
        nodes_detached_that_have_prerequisites = self._get_nodes_detached_that_have_prerequisite()
        if nodes_detached_that_have_prerequisites:
            raise CannotDetachLearningUnitsWhoHavePrerequisiteException(
                self.tree.root_node,
                nodes_detached_that_have_prerequisites
            )

    def _get_nodes_detached_that_have_prerequisite(self) -> Set['NodeLearningUnitYear']:
        learning_unit_nodes_removed = self.node_to_detach.get_all_children_as_learning_unit_nodes()
        if self.node_to_detach.is_learning_unit():
            learning_unit_nodes_removed.append(self.node_to_detach)

        return {node for node in learning_unit_nodes_removed if node.has_prerequisite}
