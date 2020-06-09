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
from program_management.ddd.domain.service import search_authorized_relationships_service


def create_program_tree_structure_service(root_node: 'Node') -> 'ProgramTree':
    authorized_relationships = search_authorized_relationships_service.search_authorized_relationships(
        min_count_authorized=1,
        parent_type=root_node.node_type
    )
    for authorized_relationship in authorized_relationships:
        new_node = Node(
            node_type=authorized_relationship.child_type.value,
            # end_date=authorized_relationship,
            # children: List['Link'] = None,
            # code: str = None,
            # title: str = None,
            # year: int = None,
            # credits: Decimal = None
            # constraint_type: ConstraintTypes = None,
            # min_constraint: int = None,
            # max_constraint: int = None,
            # remark_fr: str = None,
            # remark_en: str = None,Link
            # start_year: int = None,
            # end_year: int = None,
            # offer_title_fr: str = None,
            # offer_title_en: str = None,
            # group_title_fr: str = None,
            # group_title_en: str = None,
            # offer_partial_title_fr: str = None,
            # offer_partial_title_en: str = None,
            # category: GroupType = None,
            # management_entity_acronym: str = None,
            # teaching_campus: str = None,
            # schedule_type: ScheduleTypeEnum = None,
            # offer_status: ActiveStatusEnum = None,
            # keywords: str = None,
        )
        LinkFactory().get_link(parent=root_node, child=new_node)
    program_tree = ProgramTree(root_node=root_node)
    return program_tree