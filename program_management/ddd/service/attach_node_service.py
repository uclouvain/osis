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

from base.models.enums.link_type import LinkTypes
from program_management.ddd.contrib.validation import BusinessValidationMessage, MessageLevel, BusinessListValidator
from program_management.ddd.domain.node import Node
from program_management.ddd.domain.program_tree import ProgramTree
from program_management.ddd.validators._router import get_business_validator
from django.utils.translation import gettext as _

from program_management.ddd.repositories import fetch_tree
#
#
# class AttachNodeService:
#     business_validator: BusinessListValidator = None
#
#     def __init__(self, tree: ProgramTree, node: Node, path: str = None):
#         position_to_attach = tree.get_node(path)
#         self.business_validator = get_business_validator("attach_node", validators_args=(tree, node, position_to_attach))
#
#     def execute(self) -> List[BusinessValidationMessage]:
#         return
#
from program_management.ddd.validators._validator_groups import AttachNodeValidatorList
from program_management.ddd.validators.authorized_relationship import AttachAuthorizedRelationshipValidator


def attach_node(tree: ProgramTree, node: Node, path: str = None) -> List[BusinessValidationMessage]:
    error_messages = __validate_trees_using_node_as_reference_link(tree, node, path)

    validator = AttachNodeValidatorList(tree, node, path)
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
    child_node = tree.get_node(path)
    trees = fetch_tree.fetch_trees_from_children([child_node.node_id], link_type=LinkTypes.REFERENCE)
    for tree in trees:
        for parent_from_reference_link in tree.get_parents_as_reference_link(child_node):
            validator = AttachAuthorizedRelationshipValidator(tree, node_to_attach, parent_from_reference_link)
            if not validator.is_valid():
                error_messages += validator.error_messages
    return error_messages
