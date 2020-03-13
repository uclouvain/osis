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

from base.models.authorized_relationship import AuthorizedRelationshipList
from program_management.ddd.business_types import *
from program_management.ddd.domain.program_tree import ProgramTree

STANDARD = ""


class ProgramTreeVersionFactory:

    def copy_from(
            self,
            from_tree: 'ProgramTreeVersion',
            **tree_version_attrs
    ):
        assert isinstance(from_tree, ProgramTree)
        assert from_tree.is_standard, "Forbidden to copy from a non Standard version"
        if from_tree.is_transition:
            tree = self._copy_from_transition(from_tree, **tree_version_attrs)
        else:
            tree = self._copy_from_standard(from_tree, **tree_version_attrs)
        return tree

    def get_tree(self, **tree_attrs):
        return ProgramTreeVersion(**tree_attrs)

    def _copy_from_transition(self, from_tree: 'ProgramTreeVersion', **tree_version_attrs) -> 'ProgramTreeVersion':
        raise NotImplementedError()

    def _copy_from_standard(self, from_tree: 'ProgramTreeVersion', **tree_version_attrs) -> 'ProgramTreeVersion':
        raise NotImplementedError()


factory = ProgramTreeVersionFactory()


class ProgramTreeVersion(ProgramTree):

    def __init__(
            self,
            root_node: 'Node',
            version_name: str = STANDARD,
            is_transition: bool = False,
            authorized_relationships: AuthorizedRelationshipList = None
    ):
        super(ProgramTreeVersion, self).__init__(root_node, authorized_relationships=authorized_relationships)
        self.is_transition = is_transition
        self.version_name = version_name

    @property
    def is_standard(self):
        return self.version_name == STANDARD
