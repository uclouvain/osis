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
import copy
import functools
import itertools
from collections import Counter
from typing import List, Set, Dict, Any

import typing

from base.ddd.utils import business_validator
from base.models.authorized_relationship import AuthorizedRelationshipList
from base.models.enums.education_group_types import EducationGroupTypesEnum
from program_management.ddd.business_types import *
from program_management.ddd.domain.exception import ChildTypeNotAuthorizedException, \
    MaximumChildTypesReachedException, MinimumChildTypesNotRespectedException, MaximumChildTypesReachedBisException


class UpdateLinkAuthorizedRelationshipValidator(business_validator.BusinessValidator):
    def __init__(self, tree: 'ProgramTree', child_node: 'Node'):
        self.tree = tree
        self.link_updated = self.tree.root_node.get_direct_child(child_node.entity_id)

        super().__init__()

    def validate(self, *args, **kwargs):
        AuthorizedRelationshipValidator(tree=self.tree, link_upserted=self.link_updated).validate()


class PasteAuthorizedRelationshipValidator(business_validator.BusinessValidator):
    def __init__(self, tree: 'ProgramTree', node_to_paste: 'Node', parent_node: 'Node', link_type=None):
        self.tree = copy.copy(tree)
        self.parent_node = self.tree.get_node_by_code_and_year(parent_node.code, parent_node.year)
        self.link_created = self.parent_node.add_child(node_to_paste, link_type=link_type)

        super().__init__()

    def validate(self):
        AuthorizedRelationshipValidator(tree=self.tree, link_upserted=self.link_created).validate()


class AuthorizedRelationshipValidator(business_validator.BusinessValidator):
    def __init__(self, tree: 'ProgramTree', link_upserted: 'Link'):
        self.tree = tree
        self.link = link_upserted

        super().__init__()

    def validate(self, *args, **kwargs):
        if self.link.is_reference() and \
                self._is_child_a_minor_major_or_deepening_inside_a_list_minor_major_choice_parent():
            return

        if self.get_not_authorized_children_nodes():
            raise ChildTypeNotAuthorizedException(self.link.parent, self.children_nodes)

        if self.is_mandatory_child_converted_to_reference():
            raise MinimumChildTypesNotRespectedException(
                parent_node=self.link.parent,
                minimum_children_types_reached=[self.link.child.node_type]
            )

        if self.get_children_node_types_that_surpass_maximum_allowed():
            raise MaximumChildTypesReachedException(
                self.link.parent,
                self.link.child,
                self.get_children_node_types_that_surpass_maximum_allowed()
            )

    # TODO use min validator
    def is_mandatory_child_converted_to_reference(self):
        if not self.link.is_reference():
            return False

        mandatory_children_types = self.tree.get_ordered_mandatory_children_types(parent_node=self.link.parent)
        is_link_mandatory = self.link.child.node_type in mandatory_children_types

        if not is_link_mandatory:
            return False

        child_node_types = [l.child.node_type for l in self.link.parent.children if not l.is_reference()]
        has_parent_already_mandatory_child = self.link.child.node_type in child_node_types
        return not has_parent_already_mandatory_child

    # TODO make another validator that check finalities count
    @functools.lru_cache()
    def get_children_node_types_that_surpass_maximum_allowed(self) -> Set[EducationGroupTypesEnum]:
        children_nodes = self.link.parent.children_as_nodes_with_respect_to_reference_link
        finalities = list(itertools.chain.from_iterable([list(child.get_finality_list()) for child in children_nodes]))
        children_nodes += finalities

        node_types_that_surpass_capacity = get_node_types_that_are_full(
            self.tree.authorized_relationships,
            self.link.parent,
            children_nodes

        )
        children_node_types = {children_node.node_type for children_node in self.children_nodes + finalities}
        return children_node_types.intersection(node_types_that_surpass_capacity)

    @property
    def children_nodes(self) -> List['Node']:
        return [self.link.child] if not self.link.is_reference()\
            else self.link.child.children_as_nodes_with_respect_to_reference_link

    @functools.lru_cache()
    def get_not_authorized_children_nodes(self) -> Set['Node']:
        return get_unauthorized_children(self.tree.authorized_relationships, self.link.parent, self.children_nodes)

    def _is_child_a_minor_major_or_deepening_inside_a_list_minor_major_choice_parent(self):
        return self.link.parent.is_minor_major_list_choice() and self.link.child.is_minor_major_deepening()


def get_unauthorized_children(
        authorized_relationships: 'AuthorizedRelationshipList',
        parent_node: 'Node',
        children: List['Node']
) -> Set['Node']:
    return {child for child in children
            if not authorized_relationships.is_authorized(parent_node.node_type, child.node_type)}


def get_node_types_that_are_full(
        authorized_relationships: 'AuthorizedRelationshipList',
        parent_node: 'Node',
        nodes: List['Node']
) -> Set[EducationGroupTypesEnum]:
    node_type_counter = Counter([node.node_type for node in nodes])
    result = set()
    for node_type, count in node_type_counter.items():
        relationship = authorized_relationships.get_authorized_relationship(parent_node.node_type, node_type)
        max_count_authorized = relationship.max_count_authorized if relationship else 0
        if count > max_count_authorized:
            result.add(node_type)
    return result


class AuthorizedRelationshipLearningUnitValidator(business_validator.BusinessValidator):
    def __init__(self, tree: 'ProgramTree', node_to_attach: 'Node', position_to_attach_from: 'Node'):
        super().__init__()
        self.tree = tree
        self.node_to_attach = node_to_attach
        self.position_to_attach_from = position_to_attach_from

    def validate(self):
        if not self.tree.authorized_relationships.is_authorized(
                self.position_to_attach_from.node_type,
                self.node_to_attach.node_type
        ):
            raise ChildTypeNotAuthorizedException(
                parent_node=self.position_to_attach_from,
                children_nodes=[self.node_to_attach]
            )


class DetachAuthorizedRelationshipValidator(business_validator.BusinessValidator):
    def __init__(self, tree: 'ProgramTree', node_to_detach: 'Node', detach_from: 'Node'):
        super(DetachAuthorizedRelationshipValidator, self).__init__()
        self.node_to_detach = node_to_detach
        self.detach_from = detach_from
        self.tree = tree

    def validate(self):
        minimum_children_types_reached = self._get_minimum_children_types_reached(self.detach_from, self.node_to_detach)
        if minimum_children_types_reached:
            raise MinimumChildTypesNotRespectedException(self.tree.root_node, minimum_children_types_reached)

    def _get_minimum_children_types_reached(self, parent_node: 'Node', child_node: 'Node'):
        children_types_to_check = [child_node.node_type]
        if self.tree.get_link(parent_node, child_node).is_reference():
            children_types_to_check = [link_obj.child.node_type for link_obj in child_node.children]

        counter = Counter(parent_node.get_children_types(include_nodes_used_as_reference=True))

        types_minimum_reached = []
        for child_type in children_types_to_check:
            current_count = counter[child_type]
            relation = self.tree.authorized_relationships.get_authorized_relationship(parent_node.node_type, child_type)
            if not relation:
                # FIXME :: business cass to fix (cf unit test)
                continue
            if current_count == relation.min_count_authorized:
                types_minimum_reached.append(child_type)

        return types_minimum_reached


class MaximumChildrenTypeAuthorizedValidator(business_validator.BusinessValidator):
    def __init__(self, tree: 'ProgramTree', parent_node: 'Node'):
        super().__init__()
        self.tree = tree
        self.parent_node = parent_node

    def validate(self, *args, **kwargs):
        children_type_that_surpassed_maximum_authorized = self.get_children_types_that_surpass_maximum_allowed()
        if children_type_that_surpassed_maximum_authorized:
            raise MaximumChildTypesReachedBisException(self.parent_node, children_type_that_surpassed_maximum_authorized)

    def get_children_types_that_surpass_maximum_allowed(self) -> List['EducationGroupTypesEnum']:
        children_types_counter = Counter(self.parent_node.get_children_types(include_nodes_used_as_reference=True))
        return [
            children_type for children_type, number_children in children_types_counter.items()
            if self._is_maximum_children_surpassed(children_type, number_children)
        ]
    
    def _is_maximum_children_surpassed(self, children_type, number_children) -> bool:
        authorized_relationship = self.tree.authorized_relationships.get_authorized_relationship(
            self.parent_node.node_type,
            children_type
        )
        maximum_children_authorized = authorized_relationship.max_count_authorized if authorized_relationship else 0
        return number_children > maximum_children_authorized


class MinimumChildrenTypeAuthorizedValidator(business_validator.BusinessValidator):
    def __init__(self, tree: 'ProgramTree', parent_node: 'Node'):
        super().__init__()
        self.tree = tree
        self.parent_node = parent_node

    def validate(self, *args, **kwargs):
        children_type_that_are_inferior_to_minimum = self.get_children_types_that_do_not_respect_minimum()
        if children_type_that_are_inferior_to_minimum:
            raise MinimumChildTypesNotRespectedException(self.parent_node, children_type_that_are_inferior_to_minimum)

    def get_children_types_that_do_not_respect_minimum(self) -> List['EducationGroupTypesEnum']:
        children_types_counter = Counter(self.parent_node.get_children_types(include_nodes_used_as_reference=True))
        return [
            children_type for children_type, number_children in children_types_counter.items()
            if self._is_minimum_children_not_respected(children_type, number_children)
        ]

    def _is_minimum_children_not_respected(self, children_type, number_children) -> bool:
        authorized_relationship = self.tree.authorized_relationships.get_authorized_relationship(
            self.parent_node.node_type,
            children_type
        )
        minimum_children_authorized = authorized_relationship.min_count_authorized if authorized_relationship else 0
        return number_children < minimum_children_authorized


class ChildTypeValidator(business_validator.BusinessValidator):
    def __init__(self, tree: 'ProgramTree', parent_node: 'Node'):
        super().__init__()
        self.tree = tree
        self.parent_node = parent_node

    def validate(self, *args, **kwargs):
        children_not_authorized = self.get_children_not_authorized()
        if children_not_authorized:
            raise ChildTypeNotAuthorizedException(self.parent_node, children_not_authorized)

    def get_children_not_authorized(self):
        children_nodes = self.parent_node.children_as_nodes_with_respect_to_reference_link
        return [children_node for children_node in children_nodes if self._is_an_invalid_child(children_node)]

    def _is_an_invalid_child(self, node: 'Node') -> bool:
        authorized_relationship = self.tree.authorized_relationships.get_authorized_relationship(
            self.parent_node.node_type,
            node.node_type
        )
        return authorized_relationship is None
