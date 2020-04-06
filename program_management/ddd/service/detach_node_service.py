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
from typing import List, Set

from base.ddd.utils.validation_message import BusinessValidationMessage, BusinessValidationMessageList, MessageLevel
from base.models.group_element_year import GroupElementYear
from program_management.ddd.business_types import *
from program_management.ddd.domain.program_tree import PATH_SEPARATOR
from program_management.ddd.repositories import load_tree, persist_tree
from program_management.ddd.validators._has_or_is_prerequisite import IsPrerequisiteValidator
from program_management.models.enums.node_type import NodeType

from django.utils.translation import gettext as _


# TODO :: unit tests
def detach_node(path_to_detach: 'Path', commit=True) -> BusinessValidationMessageList:
    if not path_to_detach:
        return BusinessValidationMessageList(messages=[BusinessValidationMessage(_('Invalid tree path'))])

    root_id = int(path_to_detach.split(PATH_SEPARATOR)[0])

    working_tree = load_tree.load(root_id)
    node_to_detach = working_tree.get_node(path_to_detach)

    is_valid, messages = working_tree.detach_node(path_to_detach)
    messages += __check_is_prerequisite_in_other_trees(node_to_detach=node_to_detach)

    if is_valid and commit:
        parent_path = PATH_SEPARATOR.join(path_to_detach.split(PATH_SEPARATOR)[:-1])
        persist_tree.delete_link(working_tree.get_node(parent_path), node_to_detach)  # TODO :: use the tree.persist() !

    return BusinessValidationMessageList(messages=messages)


# TODO :: 1 fichier de service par objet métier (1 prerequisite_service?)
def __check_is_prerequisite_in_other_trees(node_to_detach: 'Node') -> List['BusinessValidationMessage']:
    messages = []
    for tree in __get_trees_using_node(node_to_detach):
        node_to_detach = tree.get_node_by_id_and_class(node_to_detach.pk, node_to_detach.__class__)
        validator = IsPrerequisiteValidator(tree, node_to_detach)
        if not validator.is_valid():
            messages += validator.messages
    return messages


def __get_trees_using_node(node_to_detach: 'Node'):
    node_id = node_to_detach.pk
    if node_to_detach.is_learning_unit():
        trees = load_tree.load_trees_from_children(child_branch_ids=None, child_leaf_ids=[node_id])
    else:
        trees = load_tree.load_trees_from_children(child_branch_ids=[node_id], child_leaf_ids=None)
    return trees


# # TODO :: remove this function when switching on new Model "Element" (chidl_leaf and child_branch will disappear)
# def __get_type(path: str) -> NodeType:
#     splitted_ids = path.split(PATH_SEPARATOR)
#     child_id = int(splitted_ids[-1])
#     parent_id = int(splitted_ids[-2])
#     gey = GroupElementYear.objects.filter(
#         parent_id=parent_id,
#         child_id=child_id
#     )
#     if gey.child_branch_id:
#         return NodeType.EDUCATION_GROUP
#     elif gey.child_leaf_id:
#         return NodeType.LEARNING_UNIT
#     else:
#         raise Exception("Bad record")
