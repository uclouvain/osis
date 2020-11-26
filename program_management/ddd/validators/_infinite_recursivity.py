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
from program_management.ddd.domain.exception import CannotPasteNodeToHimselfException, CannotAttachParentNodeException


class InfiniteRecursivityTreeValidator(business_validator.BusinessValidator):

    def __init__(
            self,
            tree: 'ProgramTree',
            node_to_add: 'Node',
            path_from_where_to_paste: 'Path',
            repository: 'ProgramTreeRepository'
    ):
        super(InfiniteRecursivityTreeValidator, self).__init__()
        self.tree = tree
        self.node_to_add = node_to_add
        self.path_from_where_to_paste = path_from_where_to_paste
        self.node_to_paste = self.tree.get_node(self.path_from_where_to_paste)
        self.repository = repository

    def _get_tree_from_node_to_add(self) -> 'ProgramTree':
        from program_management.ddd.domain.program_tree import ProgramTreeIdentity  # FIXME circular import
        tree_identity = ProgramTreeIdentity(code=self.node_to_add.entity_id.code, year=self.node_to_add.entity_id.year)
        return self.repository.get(tree_identity)

    def _get_parents(self) -> Set['Node']:
        return set(self.tree.get_parents(self.path_from_where_to_paste)) | {self.node_to_paste}

    def _children_are_parents(self) -> bool:
        all_children_of_node_to_add = self._get_tree_from_node_to_add().get_all_nodes()
        parents = self._get_parents()
        return bool(all_children_of_node_to_add.intersection(parents))

    def validate(self):
        if self._children_are_parents():
            raise CannotAttachParentNodeException(self.node_to_add)


class InfiniteRecursivityLinkValidator(business_validator.BusinessValidator):

    def __init__(self, parent_node: 'Node', node_to_add: 'Node'):
        super().__init__()
        self.parent_node = parent_node
        self.node_to_add = node_to_add

    def validate(self):
        if self.node_to_add == self.parent_node:
            raise CannotPasteNodeToHimselfException(self.parent_node)
