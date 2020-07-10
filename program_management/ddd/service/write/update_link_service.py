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
from program_management.ddd import command
from program_management.ddd.domain.program_tree import ProgramTreeIdentity
from program_management.ddd.repositories.program_tree import ProgramTreeRepository


def update_link(cmd: command.UpdateLinkCommand) -> 'NodeIdentity':
    tree_id = ProgramTreeIdentity(code=cmd.parent_node_code, year=cmd.parent_node_year)
    tree = ProgramTreeRepository.get(tree_id)
    child_node = tree.root_node.get_direct_child(code=cmd.child_node_code, year=cmd.child_node_year)

    tree.root_node.update_link_of_child_node(
        child_node,
        relative_credits=cmd.relative_credits,
        access_condition=cmd.access_condition,
        is_mandatory=cmd.is_mandatory,
        block=cmd.block,
        link_type=cmd.link_type,
        comment=cmd.comment,
        comment_english=cmd.comment_english
    )
    ProgramTreeRepository.update(tree)
