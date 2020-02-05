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

from base.models.enums.education_group_types import EducationGroupTypesEnum
from program_management.ddd.domain.node import Node


class AuthorizedRelationship:
    parent_type = None  # TODO :: move EducationGroupTypesEnum from model to business
    child_type = None
    min_constraint = None
    max_constraint = None

    def __init__(
            self,
            parent_type: EducationGroupTypesEnum,
            child_type: EducationGroupTypesEnum,
            min_constraint: int,
            max_constraint: int
    ):
        self.parent_type = parent_type
        self.child_type = child_type
        self.min_constraint = min_constraint
        self.max_constraint = max_constraint


#  TODO :: unit tests functions
class AuthorizedRelationshipList:
    authorized_relationships = None

    def __init__(self, authorized_relationships: List[AuthorizedRelationship]):
        assert authorized_relationships, "You must set at least 1 authorized relation (list can't be empty)"
        assert isinstance(authorized_relationships, list)
        self.authorized_relationships = authorized_relationships

    def __get_authorized_relationship(self, parent_node: Node, child_node: Node) -> AuthorizedRelationship:
        return next(
            (
                auth_rel for auth_rel in self.authorized_relationships
                if auth_rel.child_type == child_node.node_type
                and auth_rel.parent_type == parent_node.node_type
            ),
            None
        )

    def is_authorized(self, parent_node: Node, child_node: Node) -> bool:
        return child_node.node_type in self.get_authorized_children_types(parent_node)

    def get_authorized_children_types(self, parent_node: Node) -> Set[EducationGroupTypesEnum]:
        return set(
            auth_rel.child_type for auth_rel in self.authorized_relationships
            if auth_rel.parent_type == parent_node.node_type
        )

    def is_minimum_children_types_reached(self, parent_node: Node, child_node: Node):
        auth_relation = self.__get_authorized_relationship(parent_node, child_node)
        if not auth_relation:
            return True
        current_count = parent_node.counter_child_nodes_types[child_node.node_type]
        return current_count == auth_relation.min_constraint

    def is_maximum_children_types_reached(self, parent_node: Node, child_node: Node):
        auth_relation = self.__get_authorized_relationship(parent_node, child_node)
        if not auth_relation:
            return True
        current_count = parent_node.counter_child_nodes_types[child_node.node_type]
        return current_count == auth_relation.max_constraint
