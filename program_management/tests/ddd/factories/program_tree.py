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
import itertools
from typing import Dict

import factory.fuzzy

from base.models.authorized_relationship import AuthorizedRelationshipList
from base.models.enums.education_group_types import GroupType, TrainingType
from base.models.enums.education_group_types import MiniTrainingType
from program_management.ddd.domain.program_tree import ProgramTree
from program_management.models.enums.node_type import NodeType
from program_management.tests.ddd.factories.authorized_relationship import AuthorizedRelationshipObjectFactory
from program_management.tests.ddd.factories.domain.prerequisite.prerequisite import PrerequisitesFactory
from program_management.tests.ddd.factories.domain.program_tree.program_tree_identity import ProgramTreeIdentityFactory
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeGroupYearFactory, NodeLearningUnitYearFactory


class ProgramTreeFactory(factory.Factory):

    class Meta:
        model = ProgramTree
        abstract = False

    root_node = factory.SubFactory(NodeGroupYearFactory)
    authorized_relationships = AuthorizedRelationshipList([])
    entity_id = factory.SubFactory(
        ProgramTreeIdentityFactory,
        code=factory.SelfAttribute("..root_node.code"),
        year=factory.SelfAttribute("..root_node.year")
    )
    prerequisites = factory.SubFactory(
        PrerequisitesFactory,
        context_tree=factory.SelfAttribute("..entity_id")
    )

    @staticmethod
    def produce_standard_2M_program_tree(current_year: int, end_year: int) -> 'ProgramTree':
        """Creates a 2M standard version"""

        tree_standard = ProgramTreeFactory(
            root_node__node_type=TrainingType.PGRM_MASTER_120,
            root_node__end_year=end_year,
            root_node__year=current_year,
        )
        link1 = LinkFactory(
            parent=tree_standard.root_node,
            child__node_type=GroupType.COMMON_CORE,
            child__end_year=end_year,
            child__year=current_year,
        )
        link2 = LinkFactory(
            parent=tree_standard.root_node,
            child__node_type=GroupType.FINALITY_120_LIST_CHOICE,
            child__end_year=end_year,
            child__year=current_year,
        )
        link3 = LinkFactory(
            parent=tree_standard.root_node,
            child__node_type=GroupType.OPTION_LIST_CHOICE,
            child__end_year=end_year,
            child__year=current_year,
        )
        tree_standard.root_node.children = [link1, link2, link3]

        return tree_standard

    @staticmethod
    def produce_standard_2m_tree(current_year: int, end_year: int) -> 'ProgramTree':
        tree_data = {
            "node_type": TrainingType.PGRM_MASTER_120,
            "year": current_year,
            "end_year": end_year,
            "node_id": 1,
            "children": [
                {
                    "node_type": GroupType.COMMON_CORE,
                    "year": current_year,
                    "end_year": end_year,
                    "node_id": 21,
                    "children": [
                        {
                            "node_type": GroupType.SUB_GROUP,
                            "year": current_year,
                            "end_year": end_year,
                            "node_id": 31,
                            "children": [
                                {
                                    "node_type": NodeType.LEARNING_UNIT,
                                    "year": current_year,
                                    "end_date": end_year,
                                    "node_id": 41,
                                },
                                {
                                    "node_type": NodeType.LEARNING_UNIT,
                                    "year": current_year,
                                    "end_date": end_year,
                                    "node_id": 42,
                                }
                            ]
                        },
                        {
                            "node_type": NodeType.LEARNING_UNIT,
                            "year": current_year,
                            "end_date": end_year,
                            "node_id": 32,
                        }
                    ]
                },
                {
                    "node_type": GroupType.FINALITY_120_LIST_CHOICE,
                    "year": current_year,
                    "end_year": end_year,
                    "node_id": 22,
                    "children": [
                        {
                            "node_type": TrainingType.MASTER_MD_120,
                            "year": current_year,
                            "end_year": end_year,
                            "node_id": 33,
                            "children": [
                                {
                                    "node_type": GroupType.COMMON_CORE,
                                    "year": current_year,
                                    "end_year": end_year,
                                    "node_id": 43,
                                    "children": [
                                        {
                                            "node_type": GroupType.SUB_GROUP,
                                            "year": current_year,
                                            "end_year": end_year,
                                            "node_id": 51,
                                            "children": [
                                                {
                                                    "node_type": NodeType.LEARNING_UNIT,
                                                    "year": current_year,
                                                    "end_date": end_year,
                                                    "node_id": 61,
                                                },
                                            ]
                                        },
                                    ]
                                },
                                {
                                    "node_type": GroupType.OPTION_LIST_CHOICE,
                                    "year": current_year,
                                    "end_year": end_year,
                                    "node_id": 44,
                                    "children": [
                                        {
                                            "node_type": MiniTrainingType.OPTION,
                                            "year": current_year,
                                            "end_year": end_year,
                                            "code": "LOPTION2112",
                                            "node_id": 52,
                                        },
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "node_type": GroupType.OPTION_LIST_CHOICE,
                    "year": current_year,
                    "end_year": end_year,
                    "node_id": 23,
                    "children": [
                        {
                            "node_type": MiniTrainingType.OPTION,
                            "year": current_year,
                            "end_year": end_year,
                            "code": "LOPTION2112",
                            "node_id": 52,
                        },
                    ]
                },
                {
                    "node_type": GroupType.COMPLEMENTARY_MODULE,
                    "year": current_year,
                    "end_year": end_year,
                    "node_id": 24,
                    "children": [
                        {
                            "node_type": NodeType.LEARNING_UNIT,
                            "year": current_year,
                            "end_date": end_year,
                            "node_id": 34,
                        },
                        {
                            "node_type": NodeType.LEARNING_UNIT,
                            "year": current_year,
                            "end_date": end_year,
                            "node_id": 35,
                        },
                    ]
                },
            ]

        }
        return tree_builder(tree_data)

    @staticmethod
    def produce_bachelor_tree(current_year: int, end_year: int) -> 'ProgramTree':
        tree_data = {
            "node_type": TrainingType.BACHELOR,
            "year": current_year,
            "end_year": end_year,
            "node_id": 1,
            "children": [
                {
                    "node_type": GroupType.COMMON_CORE,
                    "year": current_year,
                    "end_year": end_year,
                    "node_id": 21,
                    "children": [
                        {
                            "node_type": GroupType.SUB_GROUP,
                            "year": current_year,
                            "end_year": end_year,
                            "node_id": 31,
                            "children": [
                                {
                                    "node_type": NodeType.LEARNING_UNIT,
                                    "year": current_year,
                                    "end_date": end_year,
                                    "node_id": 41,
                                },
                                {
                                    "node_type": NodeType.LEARNING_UNIT,
                                    "year": current_year,
                                    "end_date": end_year,
                                    "node_id": 42,
                                }
                            ]
                        }
                    ]
                },
                {
                    "node_type": GroupType.MINOR_LIST_CHOICE,
                    "year": current_year,
                    "end_year": end_year,
                    "node_id": 22,
                    "children": [
                        {
                            "node_type": MiniTrainingType.DEEPENING,
                            "year": current_year,
                            "end_year": end_year,
                            "node_id": 32,
                            "children": [
                                {
                                    "node_type": GroupType.COMMON_CORE,
                                    "year": current_year,
                                    "end_year": end_year,
                                    "node_id": 1211,
                                    "children": [
                                        {
                                            "node_type": GroupType.SUB_GROUP,
                                            "year": current_year,
                                            "end_year": end_year,
                                            "node_id": 43,
                                            "children": [
                                                {
                                                    "node_type": NodeType.LEARNING_UNIT,
                                                    "year": current_year,
                                                    "end_date": end_year,
                                                    "node_id": 51,
                                                },
                                                {
                                                    "node_type": NodeType.LEARNING_UNIT,
                                                    "year": current_year,
                                                    "end_date": end_year,
                                                    "node_id": 52,
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                    ]
                },
                {"node_type": NodeType.LEARNING_UNIT}
            ]
        }
        return tree_builder(tree_data)


def _tree_builder(data: Dict) -> 'Node':
    _data = data.copy()
    children = _data.pop("children", [])

    node = _node_builder(_data)

    for child_data, order in zip(children, itertools.count()):
        link_data = child_data.pop("link_data", {})
        child_node = _tree_builder(child_data)
        LinkFactory(parent=node, child=child_node, **link_data, order=order)

    return node


def _node_builder(data: Dict) -> 'Node':
    node_factory = NodeGroupYearFactory
    if data["node_type"] == NodeType.LEARNING_UNIT:
        node_factory = NodeLearningUnitYearFactory
    return node_factory(**data)


def _build_authorized_relationships(root_node: 'Node') -> 'AuthorizedRelationshipList':
    all_links = root_node.get_all_children()
    relationships = [
        AuthorizedRelationshipObjectFactory(
            parent_type=link.parent.node_type,
            child_type=link.child.node_type,
            min_count_authorized=0,
            max_count_authorized=10
        )
        for link in all_links
    ]
    return AuthorizedRelationshipList(relationships)


def tree_builder(data: Dict) -> 'ProgramTree':
    root_node = _tree_builder(data)
    authorized_relationships = _build_authorized_relationships(root_node)
    return ProgramTreeFactory(root_node=root_node, authorized_relationships=authorized_relationships)
