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
import functools
from collections import Counter
from typing import List, Set, Optional

from django.utils.translation import gettext as _

import osis_common.ddd.interface
from base.ddd.utils import business_validator
from base.models.authorized_relationship import AuthorizedRelationshipList
from base.models.enums import education_group_types
from base.models.enums.education_group_types import EducationGroupTypesEnum
from base.models.enums.link_type import LinkTypes
from program_management.ddd.business_types import *
from program_management.ddd.domain.exception import ChildTypeNotAuthorizedException, \
    MaximumChildTypesReachedException


class UpdateLinkAuthorizedRelationshipValidator(business_validator.BusinessValidator):
    def __init__(self, tree: 'ProgramTree', node_to_update_link_with: 'Node', link_type: Optional[LinkTypes]):
        self.tree = tree
        self.parent_node = tree.root_node
        self.node_to_update_link_with = node_to_update_link_with
        self.link_type = link_type

        super().__init__()

    def validate(self, *args, **kwargs):
        if self.is_link_type_reference() and \
                self._is_child_a_minor_major_or_option_inside_a_list_minor_major_option_choice_parent():
            return

        if self.get_not_authorized_children_nodes():
            raise ChildTypeNotAuthorizedException(self.parent_node, self.children_nodes)

        if self.get_children_node_types_that_surpass_maximum_allowed():
            raise MaximumChildTypesReachedException(
                self.parent_node,
                self.node_to_update_link_with,
                self.get_children_node_types_that_surpass_maximum_allowed()
            )

    @property
    def children_nodes(self) -> List['Node']:
        return [self.node_to_update_link_with] if not self.is_link_type_reference() \
            else self.node_to_update_link_with.children_as_nodes_with_respect_to_reference_link

    @functools.lru_cache()
    def get_children_node_types_that_surpass_maximum_allowed(self) -> Set[EducationGroupTypesEnum]:
        node_types_that_surpass_capacity = get_node_types_that_are_full(
            self.tree.authorized_relationships,
            self.parent_node,
            self.parent_node.children_as_nodes_with_respect_to_reference_link
        )
        children_node_types = {children_node.node_type for children_node in self.children_nodes}
        return children_node_types.intersection(node_types_that_surpass_capacity)

    def is_link_type_reference(self):
        return self.link_type == LinkTypes.REFERENCE

    def _is_child_a_minor_major_or_option_inside_a_list_minor_major_option_choice_parent(self):
        return self.parent_node.node_type in education_group_types.GroupType.minor_major_list_choice_enums() and \
               self.node_to_update_link_with.node_type in education_group_types.MiniTrainingType

    @functools.lru_cache()
    def get_not_authorized_children_nodes(self) -> Set['Node']:
        return get_unauthorized_children(self.tree.authorized_relationships, self.parent_node, self.children_nodes)


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
        max_count_authorized = authorized_relationships.get_authorized_relationship(parent_node.node_type, node_type)
        if count > max_count_authorized.max_count_authorized:
            result.add(node_type)
    return result


class PasteAuthorizedRelationshipValidator(business_validator.BusinessValidator):
    def __init__(self, tree: 'ProgramTree', node_to_paste: 'Node', node_to_paste_into: 'Node', link_type=None):
        super(PasteAuthorizedRelationshipValidator, self).__init__()
        self.tree = tree
        self.node_to_paste = node_to_paste
        self.parent = node_to_paste_into
        self.auth_relations = tree.authorized_relationships
        self.link_type = link_type
        self.nodes_to_paste = [self.node_to_paste] if link_type != LinkTypes.REFERENCE \
            else self.node_to_paste.children_as_nodes_with_respect_to_reference_link

    def validate(self):
        if self.parent.is_minor_major_option_list_choice() and\
                not self.node_to_paste.is_minor_major_option_list_choice():
            return
        if self.are_types_not_authorized():
            raise ChildTypeNotAuthorizedException(self.parent, self._get_not_authorized_children())

        if self.are_maximum_children_types_reached():
            raise MaximumChildTypesReachedException(
                self.parent,
                self.node_to_paste,
                self._get_maximum_children_types_reached()
            )

    def are_types_not_authorized(self) -> bool:
        return bool(self._get_not_authorized_children())

    def _get_not_authorized_children(self) -> List['Node']:
        return [
            node_to_paste
            for node_to_paste in self.nodes_to_paste
            if not self.tree.authorized_relationships.is_authorized(
                parent_type=self.parent.node_type,
                child_type=node_to_paste.node_type
            )
        ]

    def are_maximum_children_types_reached(self) -> bool:
        return bool(self._get_maximum_children_types_reached())

    def _get_maximum_children_types_reached(self) -> List:
        return [node_to_paste.node_type for node_to_paste in self.nodes_to_paste
                if self.is_maximum_children_types_reached(self.parent, node_to_paste)]

    def is_maximum_children_types_reached(self, parent_node: 'Node', child_node: 'Node'):
        if not self.auth_relations.is_authorized(parent_node.node_type, child_node.node_type):
            return False
        counter = Counter(parent_node.get_children_types(include_nodes_used_as_reference=True))
        current_count = counter[child_node.node_type]
        relation = self.auth_relations.get_authorized_relationship(parent_node.node_type, child_node.node_type)
        return current_count >= relation.max_count_authorized


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
            raise osis_common.ddd.interface.BusinessExceptions([
                _("The parent must have at least one child of type(s) \"%(types)s\".") % {
                    "types": ','.join(str(node_type.value) for node_type in minimum_children_types_reached)
                }
            ])

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
