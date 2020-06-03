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

from base.ddd.utils import business_validator
from base.ddd.utils.validation_message import BusinessValidationMessageList
from program_management.ddd import command
from program_management.ddd.domain.program_tree import PATH_SEPARATOR
from program_management.ddd.repositories import load_tree, persist_tree
from program_management.ddd.service import tree_service
from program_management.ddd.validators._detach_option_2M import DetachOptionValidator


def detach_node(detach_command: command.DetachNodeCommand) -> BusinessValidationMessageList:
    path_to_detach = detach_command.path
    commit = detach_command.commit

    root_id = int(path_to_detach.split(PATH_SEPARATOR)[0])
    working_tree = load_tree.load(root_id)
    node_to_detach = working_tree.get_node(path_to_detach)

    other_trees_using_node = [
        tree for tree in tree_service.search_trees_using_node(node_to_detach) if tree != working_tree
    ]

    messages = []
    messages += __check_detach_option(working_tree, path_to_detach, other_trees_using_node)

    is_valid, _messages = working_tree.detach_node(path_to_detach)
    messages += _messages

    message_list = BusinessValidationMessageList(messages=messages)

    if not message_list.contains_errors() and commit:
        persist_tree.persist(working_tree)

    return message_list


def __check_detach_option(working_tree, path_to_detach, trees_using_node) -> List[str]:
    try:
        DetachOptionValidator(working_tree, path_to_detach, trees_using_node).validate()
    except business_validator.BusinessExceptions as business_exceptions:
        return business_exceptions.messages
    return []
