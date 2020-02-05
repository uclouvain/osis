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
from collections import Counter
from typing import List

from base.models.enums.education_group_types import EducationGroupTypesEnum
from base.models.enums.link_type import LinkTypes
from program_management.DomainDrivenDesign.domain.link import Link, factory as link_factory
from program_management.DomainDrivenDesign.domain.prerequisite import Prerequisite
from program_management.models.enums import node_type


class NodeFactory:
    def get_node(self, type, **kwargs):
        node_cls = {
            node_type.EDUCATION_GROUP: NodeEducationGroupYear,   # TODO: Remove when migration is done

            node_type.GROUP: NodeGroupYear,
            node_type.LEARNING_UNIT: NodeLearningUnitYear,
            node_type.LEARNING_CLASS: NodeLearningClassYear
        }[type]
        return node_cls(**kwargs)


factory = NodeFactory()


class Node:

    children = None
    node_type = None  # TODO :: rename to 'type'

    def __init__(self, node_id: int, node_type: EducationGroupTypesEnum = None, children: List[Link] = None):
        self.node_id = node_id
        if children is None:
            children = []
        self.children = children
        self.node_type = node_type

    def __eq__(self, other):
        return self.node_id == other.node_id

    @property
    def pk(self):
        return self.node_id

    @property
    def children_types(self) -> List[EducationGroupTypesEnum]:
        list_child_nodes_types = []
        for link in self.children:
            if link.link_type == LinkTypes.REFERENCE.name:
                childs_of_child = link.child.children
                list_child_nodes_types += [link.child.node_type for link in childs_of_child]
            else:
                list_child_nodes_types.append(link.child.node_type)
        return list_child_nodes_types

    @property
    def descendents(self):
        return _get_descendents(self)

    @property
    def counter_child_nodes_types(self) -> Counter:
        return Counter(self.children_types)

    def add_child(self, node, **kwargs):
        child = link_factory.get_link(parent=self, child=node, **kwargs)
        self.children.append(child)

    def detach_child(self, node_id):
        self.children = [link for link in self.children if link.child.pk == node_id]


def _get_descendents(root_node: Node, current_path: str = None):
    _descendents = {}
    if current_path is None:
        current_path = str(root_node.pk)

    for link in root_node.children:
        child_path = "|".join([current_path, str(link.child.pk)])
        _descendents = {
            **{child_path: link.child},
            **_get_descendents(link.child, current_path=child_path)
        }
    return _descendents


class NodeEducationGroupYear(Node):
    def __init__(self, node_id: int, acronym, title, year, children: List[Link] = None, **kwargs):
        super().__init__(node_id, children)
        self.acronym = acronym
        self.title = title
        self.year = year


class NodeGroupYear(Node):
    def __init__(self, node_id: int, acronym, title, year, children: List[Link] = None, **kwargs):
        super().__init__(node_id, children)
        self.acronym = acronym
        self.title = title
        self.year = year


class NodeLearningUnitYear(Node):
    def __init__(self, node_id: int, acronym, title, year, proposal_type=None, **kwargs):
        super().__init__(node_id)
        self.acronym = acronym
        self.title = title
        self.year = year
        self.proposal_type = proposal_type
        self.prerequisite = None
        self.is_prerequisite_of = []

    @property
    def has_prerequisite(self):
        return bool(self.prerequisite)

    @property
    def is_prerequisite(self):
        return bool(self.is_prerequisite_of)

    @property
    def has_proposal(self):
        return bool(self.proposal_type)

    def set_prerequisite(self, prerequisite: Prerequisite):
        self.prerequisite = prerequisite


class NodeLearningClassYear(Node):
    def __init__(self, node_id: int, year, children: List[Link] = None):
        super().__init__(node_id, children)
        self.year = year


class NodeNotFoundException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__("The node cannot be found on the current tree")
