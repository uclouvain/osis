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
from typing import List

import program_management.ddd.command
from base.models.enums.link_type import LinkTypes
from program_management.ddd.repositories import load_tree, load_node, persist_tree
from program_management.ddd.validators._attach_finality_end_date import AttachFinalityEndDateValidator
from program_management.ddd.validators._attach_option import AttachOptionsValidator
from program_management.ddd.validators._authorized_relationship import AttachAuthorizedRelationshipValidator
from program_management.models.enums.node_type import NodeType


def paste_element_service(attach_command: program_management.ddd.command.AttachNodeCommand) -> List['BusinessValidationMessage']:
    root_id = attach_command.root_id
    type_node_to_attach = attach_command.type_of_node_to_attach
    node_id_to_attach = attach_command.node_id_to_attach
    path = attach_command.path_where_to_attach
    commit = attach_command.commit

    tree = load_tree.load(root_id)
    node_to_attach = load_node.load_by_type(type_node_to_attach, element_id=node_id_to_attach)

    error_messages = __validate_trees_using_node_as_reference_link(tree, node_to_attach, path)
    if type_node_to_attach != NodeType.LEARNING_UNIT:
        error_messages += _validate_end_date_and_option_finality(node_to_attach)
    if error_messages:
        return error_messages
    success_messages = tree.attach_node(node_to_attach, path, attach_command)
    if commit:
        persist_tree.persist(tree)
    return success_messages


def __validate_trees_using_node_as_reference_link(
        tree: 'ProgramTree',
        node_to_attach: 'Node',
        path: 'Path'
) -> List['BusinessValidationMessage']:

    error_messages = []
    child_node = tree.get_node(path)
    trees = load_tree.load_trees_from_children([child_node.node_id], link_type=LinkTypes.REFERENCE)
    for tree in trees:
        for parent_from_reference_link in tree.get_parents_using_node_as_reference(child_node):
            validator = AttachAuthorizedRelationshipValidator(tree, node_to_attach, parent_from_reference_link)
            if not validator.is_valid():
                error_messages += validator.error_messages
    return error_messages


def _validate_end_date_and_option_finality(node_to_attach: 'Node') -> List['BusinessValidationMessage']:
    error_messages = []
    tree_from_node_to_attach = load_tree.load(node_to_attach.node_id)
    finality_ids = [n.node_id for n in tree_from_node_to_attach.get_all_finalities()]
    if node_to_attach.is_finality() or finality_ids:
        trees_2m = [
            tree for tree in load_tree.load_trees_from_children(child_branch_ids=finality_ids)
            if tree.is_master_2m()
        ]
        for tree_2m in trees_2m:
            validator = AttachFinalityEndDateValidator(tree_2m, tree_from_node_to_attach)
            if not validator.is_valid():
                error_messages += validator.error_messages
            validator = AttachOptionsValidator(tree_2m, tree_from_node_to_attach)
            if not validator.is_valid():
                error_messages += validator.error_messages
    return error_messages