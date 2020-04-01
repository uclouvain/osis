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
from program_management.ddd.domain import node, link


def up_link(node_obj: node.Node, link_to_up: link.Link):
    previous_order = link_to_up.order - 1
    if not previous_order >= 0:
        return
    link_to_down = node_obj.children[previous_order]
    link_to_up.order_up()
    link_to_down.order_down()


def down_link(node_obj: node.Node, link_to_down: link.Link):
    next_order = link_to_down.order + 1
    if not len(node_obj.children) > next_order:
        return
    link_to_up = node_obj.children[next_order]
    link_to_up.order_up()
    link_to_down.order_down()

