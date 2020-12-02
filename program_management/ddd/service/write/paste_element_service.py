# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
# ############################################################################
from django.db import transaction

from program_management.ddd import command
from program_management.ddd.business_types import *
from program_management.ddd.domain import node
from program_management.ddd.domain.exception import ProgramTreeNotFoundException
from program_management.ddd.domain.program_tree import PATH_SEPARATOR, ProgramTreeIdentity
from program_management.ddd.domain.service import identity_search
from program_management.ddd.repositories import load_tree, program_tree, \
    program_tree_version, node as node_repository


@transaction.atomic()
def paste_element(paste_command: command.PasteElementCommand) -> 'LinkIdentity':
    node_identity = node.NodeIdentity(code=paste_command.node_to_paste_code, year=paste_command.node_to_paste_year)

    path_to_detach = paste_command.path_where_to_detach

    root_id = int(paste_command.path_where_to_paste.split("|")[0])
    program_tree_identity = identity_search.ProgramTreeIdentitySearch().get_from_element_id(root_id)
    tree = program_tree.ProgramTreeRepository.get(program_tree_identity)

    #  Search program tree if possible to fetch also children of node to paste
    try:
        node_to_attach = program_tree.ProgramTreeRepository.get(
            ProgramTreeIdentity(code=paste_command.node_to_paste_code, year=paste_command.node_to_paste_year)
        ).root_node
    except ProgramTreeNotFoundException:
        node_to_attach = node_repository.NodeRepository.get(node_identity)

    link_created = tree.paste_node(
        node_to_attach,
        paste_command,
        program_tree.ProgramTreeRepository(),
        program_tree_version.ProgramTreeVersionRepository()
    )

    program_tree.ProgramTreeRepository().update(tree)

    if path_to_detach:
        root_tree_to_detach = int(path_to_detach.split(PATH_SEPARATOR)[0])
        tree_to_detach = tree if root_tree_to_detach == root_id else load_tree.load(root_tree_to_detach)
        tree_to_detach.detach_node(path_to_detach, program_tree.ProgramTreeRepository())
        program_tree.ProgramTreeRepository().update(tree_to_detach)

    return link_created.entity_id
