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

from program_management.DomainDrivenDesign.contrib.validation import BusinessValidationMessage, MessageLevel
from program_management.DomainDrivenDesign.domain.node import Node
from program_management.DomainDrivenDesign.domain.program_tree import ProgramTree
from program_management.DomainDrivenDesign.validators import attach_node as attach_node_validator
from django.utils.translation import gettext as _

from program_management.DomainDrivenDesign.validators.attach_node import AuthorizedRelationshipValidator
from program_management.DomainDrivenDesign.repositories import fetch_tree


def attach_node(tree: ProgramTree, node: Node, path: str = None) -> List[BusinessValidationMessage]:
    position_to_attach = tree.get_node(path)

    error_messages = __validate_trees_using_node_as_reference_link(tree, node, path)

    validator = attach_node_validator.factory.get_attach_node_validator(tree, node, position_to_attach)
    validator.validate()
    error_messages += validator.error_messages

    if not error_messages:
        return [BusinessValidationMessage(_('Success message'), MessageLevel.SUCCESS)]

    return error_messages


def __validate_trees_using_node_as_reference_link(
        tree: ProgramTree,
        node_to_attach: Node,
        path: str
) -> List[BusinessValidationMessage]:
    error_messages = []
    for tree in __get_trees_using_node_as_reference(tree.get_node(path)):
        validator = AuthorizedRelationshipValidator(tree, node_to_attach, path)
        validator.validate()
        error_messages += validator.error_messages
    return error_messages


def __get_trees_using_node_as_reference(node: Node) -> List[ProgramTree]:
    # TODO :: filter children with only link==REFERENCE
    children_ids = [node.node_id]
    return fetch_tree.fetch_trees_from_children(children_ids)
