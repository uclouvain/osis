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
from program_management.ddd.business_types import *
from program_management.ddd.domain.link import LinkFactory
from program_management.ddd.domain.node import NodeFactory
from program_management.ddd.domain.service import search_authorized_relationships_service


def create_program_tree_structure(from_tree: 'ProgramTree') -> 'ProgramTree':
    child_types = search_authorized_relationships_service.search_authorized_relationships(
        min_count_authorized=1,
        parent_type=from_tree.root_node.node_type
    )
    children_node_list = from_tree.root_node.get_all_children_as_nodes(take_only=child_types)
    for child in children_node_list:
        new_node = NodeFactory().deepcopy_node_without_copy_children_recursively(original_node=child)
        LinkFactory().get_link(parent=from_tree.root_node, child=new_node)
    program_tree = ProgramTree(root_node=from_tree.root_node)
    return program_tree
