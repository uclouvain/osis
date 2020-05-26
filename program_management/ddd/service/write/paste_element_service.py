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

from program_management.ddd.business_types import *
from program_management.ddd import command
from program_management.ddd.repositories import load_tree, load_node, persist_tree
from program_management.ddd.service import detach_node_service
from program_management.ddd.validators._authorized_relationship_for_all_trees import \
    __validate_trees_using_node_as_reference_link
from program_management.ddd.validators._validate_end_date_and_option_finality import \
    _validate_end_date_and_option_finality
from program_management.models.enums.node_type import NodeType


def paste_element_service(paste_command: command.PasteElementCommand) -> List['BusinessValidationMessage']:
    root_id = paste_command.root_id
    type_node_to_attach = paste_command.node_to_paste_type
    node_id_to_attach = paste_command.node_to_paste_id
    path = paste_command.path_where_to_paste
    path_to_detach = paste_command.path_where_to_detach
    commit = paste_command.commit

    tree = load_tree.load(root_id)
    node_to_attach = load_node.load_by_type(type_node_to_attach, element_id=node_id_to_attach)

    error_messages = __validate_trees_using_node_as_reference_link(tree, node_to_attach, path)
    if type_node_to_attach != NodeType.LEARNING_UNIT:
        error_messages += _validate_end_date_and_option_finality(node_to_attach)
    if error_messages:
        return error_messages

    action_messages = []
    if path_to_detach:

        action_messages.extend(detach_node_service.detach_node(path_to_detach, commit=commit).errors)

    action_messages.extend(tree.paste_node(node_to_attach, paste_command))
    if commit:
        persist_tree.persist(tree)
    return action_messages
