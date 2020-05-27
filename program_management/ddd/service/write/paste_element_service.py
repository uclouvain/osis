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

from program_management.ddd import command
from program_management.ddd.business_types import *
from program_management.ddd.repositories import load_tree, load_node, persist_tree
from program_management.ddd.service import detach_node_service


# TODO should return an entity
def paste_element_service(paste_command: command.PasteElementCommand) -> List['BusinessValidationMessage']:
    commit = paste_command.commit
    path_to_detach = paste_command.path_where_to_detach
    tree = load_tree.load(paste_command.root_id)
    node_to_attach = load_node.load_by_type(paste_command.node_to_paste_type, element_id=paste_command.node_to_paste_id)

    action_messages = []
    if path_to_detach:
        action_messages.extend(detach_node_service.detach_node(path_to_detach, commit=commit).errors)

    action_messages.extend(tree.paste_node(node_to_attach, paste_command))

    if commit:
        persist_tree.persist(tree)
    return action_messages
