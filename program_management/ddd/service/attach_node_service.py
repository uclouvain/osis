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
import collections
from typing import List, Tuple

from django.utils.translation import gettext_lazy as _

from base.models.enums.link_type import LinkTypes
from osis_common.decorators.deprecated import deprecated
from program_management.ddd.business_types import *
from program_management.ddd.repositories import load_tree, persist_tree, load_node
from program_management.ddd.validators import link as link_validator, _minimum_editable_year, _infinite_recursivity
from program_management.ddd.validators._attach_finality_end_date import AttachFinalityEndDateValidator
from program_management.ddd.validators._attach_option import AttachOptionsValidator
from program_management.ddd.validators._authorized_relationship import AttachAuthorizedRelationshipValidator
from program_management.models.enums.node_type import NodeType

AttachRequest = collections.namedtuple(
    "AttachRequest",
    "access_condition, is_mandatory, block, link_type, comment, comment_english, relative_credits"
)


def attach_node(
        root_id: int,
        node_id_to_attach: int,
        type_node_to_attach,
        path: 'Path',
        attach_request: AttachRequest,
        commit=True,
) -> List['BusinessValidationMessage']:
    tree = load_tree.load(root_id)
    node_to_attach = load_node.load_by_type(type_node_to_attach, element_id=node_id_to_attach)
    error_messages = __validate_trees_using_node_as_reference_link(tree, node_to_attach, path)
    if type_node_to_attach != NodeType.LEARNING_UNIT:
        error_messages += _validate_end_date_and_option_finality(node_to_attach)
    if error_messages:
        return error_messages
    success_messages = tree.attach_node(node_to_attach, path, **attach_request._asdict())
    if commit:
        persist_tree.persist(tree)
    return success_messages


#  FIXME suppress when view MoveGroupElementYear will use ddd services
@deprecated
def check_attach_via_parent(
        parent_node_id: int,
        children_nodes_ids: List[int],
        children_type: NodeType
) -> List['BusinessValidationMessage']:
    result = []

    parent_node = load_tree.load_node.load_by_type(NodeType.EDUCATION_GROUP, parent_node_id)
    children_nodes = [load_node.load_by_type(children_type, node_id) for node_id in children_nodes_ids]

    for child_node in children_nodes:
        if children_type != NodeType.LEARNING_UNIT:
            result.extend(_validate_end_date_and_option_finality(child_node))

        validator = link_validator.CreateLinkValidatorList(parent_node, child_node)
        if not validator.is_valid():
            result.extend(validator.messages)

    return result


def check_attach(
        tree_root_id: int,
        path_of_node_to_attach_from: 'Path',
        nodes_to_attach: List[Tuple[int, NodeType]]
) -> List['BusinessValidationMessage']:
    result = []
    tree = load_tree.load(tree_root_id)
    node_to_attach_from = tree.get_node(path_of_node_to_attach_from)

    _nodes_to_attach = [load_node.load_by_type(node_type, node_id) for node_id, node_type in nodes_to_attach]

    if not _nodes_to_attach:
        result.append(
            _("Please select an item before adding it")
        )

    for node_to_attach in _nodes_to_attach:
        if not node_to_attach.is_learning_unit():
            result.extend(_validate_end_date_and_option_finality(node_to_attach))

        validator = link_validator.CreateLinkValidatorList(node_to_attach_from, node_to_attach)
        if not validator.is_valid():
            result.extend(validator.messages)

        validator = _minimum_editable_year.MinimumEditableYearValidator(tree)
        if not validator.is_valid():
            result.extend(validator.messages)

        validator = _infinite_recursivity.InfiniteRecursivityTreeValidator(
            tree,
            node_to_attach,
            path_of_node_to_attach_from
        )
        if not validator.is_valid():
            result.extend(validator.messages)

    return result


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
