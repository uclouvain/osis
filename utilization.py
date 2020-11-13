import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backoffice.settings.local")
django.setup()

from collections import defaultdict
from typing import Dict, List, Any

from django.urls import reverse

from program_management.ddd.business_types import *
from program_management.ddd.command import GetProgramTreesFromNodeCommand
from program_management.ddd.domain.node import NodeGroupYear, NodeIdentity
from program_management.ddd.domain.program_tree import get_nearest_parents
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.ddd.service.read import search_program_trees_using_node_service
from program_management.serializers.node_view import get_program_tree_version_name, get_program_tree_version_dict
from program_management.ddd.repositories.node import NodeRepository

IndirectParentNode = NodeGroupYear


def get_utilization_rows(acronym: str, year: int) -> Dict['Node', List['IndirectParentNode']]:

    node_identity = NodeIdentity(code=acronym, year=year)
    cmd = GetProgramTreesFromNodeCommand(code=node_identity.code, year=node_identity.year)
    program_trees = search_program_trees_using_node_service.search_program_trees_using_node(cmd)
    direct_parents = get_direct_parents(node_identity, program_trees)

    utilizations = {}
    for direct_parent in direct_parents:
        utilizations[direct_parent] = _get_indirect_parents(direct_parent, program_trees)

    return utilizations


def _get_indirect_parents(direct_parent: 'Node', program_trees: List['ProgramTree']) -> List['NodeGroupYear']:
    trees_using_direct_parent = [tree for tree in program_trees if tree.node_contains_usage(direct_parent)]
    indirect_parents = []
    for tree in trees_using_direct_parent:        
        indirect_parents.extend(tree.get_indirect_parents(direct_parent))
    return indirect_parents


def get_direct_parents(node_identity: 'NodeIdentity', program_trees: List['ProgramTree']) -> List['Node']:
    node = NodeRepository.get(node_identity)
    utilizations = []
    for tree in program_trees:
        direct_parent_nodes = tree.get_direct_parents_nodes_using_node(node)
        for direct_parent in direct_parent_nodes:
            utilizations.append(direct_parent)
    return set(utilizations)


get_utilization_rows('LLSMF2009', 2019)
