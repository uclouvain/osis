import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backoffice.settings.local")
django.setup()

from typing import Dict, List, Set

from program_management.ddd.business_types import *
from program_management.ddd.command import GetProgramTreesFromNodeCommand
from program_management.ddd.domain.node import NodeGroupYear, NodeIdentity
from program_management.ddd.service.read import search_program_trees_using_node_service
from program_management.ddd.repositories.node import NodeRepository

IndirectParentNode = NodeGroupYear


def get_utilization_rows(acronym: str, year: int) -> Dict['Node', List['IndirectParentNode']]:
    return _get_direct_parents(acronym, year)


def _get_direct_parents(acronym: str, year: int):
    node_identity = NodeIdentity(code=acronym, year=year)
    cmd = GetProgramTreesFromNodeCommand(code=node_identity.code, year=node_identity.year)
    program_trees = search_program_trees_using_node_service.search_program_trees_using_node(cmd)
    direct_parents = get_direct_parents(node_identity, program_trees)

    map_indirect_parents = _get_indirect_parents_nodes(direct_parents, program_trees)
    indirect_parents = []

    for k, val in map_indirect_parents.items():
        indirect_parents.extend(val)
    map_indirect_parents_level2 = _get_indirect_parents_nodes(indirect_parents, program_trees)
    return {'direct_parents': direct_parents,
            'map_indirect_parents': map_indirect_parents,
            'map_indirect_parents_level2': map_indirect_parents_level2}


def _get_indirect_parents_nodes(direct_parents: List['Node'], program_trees: List['ProgramTree']) -> Dict['Node', List['Node']]:
    utilizations = {}
    for direct_parent in direct_parents:
        utilizations[direct_parent] = _get_indirect_parents(direct_parent, program_trees)
    return utilizations


def _get_indirect_parents(direct_parent: 'Node', program_trees: List['ProgramTree']) -> List['NodeGroupYear']:
    trees_using_direct_parent = [tree for tree in program_trees if tree.node_contains_usage(direct_parent)]
    indirect_parents = []

    for tree in trees_using_direct_parent:
        node_indirect_parents = tree.get_indirect_parents(direct_parent)
        indirect_parents.extend(node_indirect_parents)
    return set(indirect_parents)


def get_direct_parents(node_identity: 'NodeIdentity', program_trees: List['ProgramTree']) -> Set['Node']:
    node = NodeRepository.get(node_identity)
    utilizations = []
    for tree in program_trees:
        direct_parent_nodes = tree.get_direct_parents_nodes_using_node(node)
        for direct_parent in direct_parent_nodes:
            utilizations.append(direct_parent)
    return set(utilizations)
