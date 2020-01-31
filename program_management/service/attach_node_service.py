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
from typing import List

from program_management.contrib.validation import BusinessValidationMessage
from program_management.domain.node import Node
from program_management.domain.program_tree import ProgramTree
from program_management.repositories import fetch_authorized_relationship
from program_management.repositories.tree.validators.attach_node import AuthorizedRelationshipValidator


def attach_node(tree: ProgramTree, node: Node, path: str = None) -> List[BusinessValidationMessage]:
    error_messages = []
    authorized_relationships = fetch_authorized_relationship.fetch()
    for tree in __get_trees_using_node_as_reference(tree.get_node(path)):
        validator = AuthorizedRelationshipValidator(tree, node, path, authorized_relationships)
        validator.validate()
        error_messages += validator.error_messages

    validator = AuthorizedRelationshipValidator(tree, node, path, authorized_relationships)
    validator.validate()
    error_messages += validator.error_messages
    # TODO :: gérer les success messages
    # TODO :: ajouter l'appel aux auxtres validators ; AuthorizedRelationshipValidator devrait se trouver dans un même BusinessListValidator ??
    return


def __get_trees_using_node_as_reference(node: Node) -> List[ProgramTree]:
    pass  # Using fetch_tree() for multiple programTree
