import itertools
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
    node_identity = NodeIdentity(code=acronym, year=year)
    cmd = GetProgramTreesFromNodeCommand(code=node_identity.code, year=node_identity.year)
    program_trees = search_program_trees_using_node_service.search_program_trees_using_node(cmd)

    links_using_node = get_direct_parents(node_identity, program_trees)

    #TODO ordonner par ordre alphobtique
    map_node_with_indirect_parents = _get_map_node_with_indirect_parents(
        direct_parents={link.parent for link in links_using_node},
        program_trees=program_trees
    )
    indirect_parents = set(itertools.chain.from_iterable(map_node_with_indirect_parents.values()))

    map_node_indirect_parents_of_indirect_parents = _get_map_node_with_indirect_parents(indirect_parents, program_trees)
    map_node_with_indirect_parents.update(map_node_indirect_parents_of_indirect_parents)

    return {
        'direct_parents': links_using_node,
        'map_node_with_indirect_parents': map_node_with_indirect_parents
    }


def _get_map_node_with_indirect_parents(
        direct_parents: Set['Node'],
        program_trees: List['ProgramTree']
) -> Dict['Node', List['Node']]:
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
    # TODO ordonner par ordre alphobtique
    return set(indirect_parents)


def get_direct_parents(node_identity: 'NodeIdentity', program_trees: List['ProgramTree']) -> Set['Link']:
    node = NodeRepository.get(node_identity)
    utilizations = set()
    for tree in program_trees:
        utilizations |= set(tree.get_links_using_node(node))
    return utilizations
