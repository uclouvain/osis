#############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
#############################################################################
from typing import List

from program_management.ddd.business_types import *
from program_management.ddd.command import GetProgramTreesFromNodeCommand
from program_management.ddd.command import SearchIndirectParentCommand
from program_management.ddd.repositories.node import NodeRepository
from program_management.ddd.service.read import search_program_trees_using_node_service
from program_management.serializers.program_trees_utilizations import _sort
from program_management.serializers.program_trees_utilizations import buid_map_node_with_indirect_parents
from program_management.ddd.domain.node import NodeIdentity


def search_indirect_parents(cmd: SearchIndirectParentCommand) -> List['Node']:
    node_repository = NodeRepository()
    cmd = GetProgramTreesFromNodeCommand(code=cmd.code, year=cmd.year)
    node_identity = NodeIdentity(code=cmd.code, year=cmd.year)
    program_trees = search_program_trees_using_node_service.search_program_trees_using_node(cmd)
    links_using_node, map_node_with_indirect_parents = buid_map_node_with_indirect_parents(node_identity,
                                                                                           node_repository,
                                                                                           program_trees)
    parents_root = set()
    for direct_link in sorted(links_using_node, key=lambda link: link.parent.code):
        root = None
        parent_node = direct_link.parent
        for indirect_parent in _sort(map_node_with_indirect_parents, direct_link.parent):
            parent_node = indirect_parent
            indirect_parents = _sort(map_node_with_indirect_parents, indirect_parent)
            if (indirect_parents is None or len(indirect_parents) == 0) or parent_node.is_minor_or_deepening():
                root = indirect_parent
                break
            else:
                for indirect_parent_of_indirect_parent in indirect_parents:
                    node = indirect_parent_of_indirect_parent
                    if parent_node.is_finality() and node.is_training():
                        root = node
                        break
        if root is None:
            root = parent_node
        parents_root.add(root)

    return parents_root
