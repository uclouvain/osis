##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from datetime import datetime
from typing import Iterable, Dict, Optional, List

import attr
from django.utils.functional import cached_property

from base.models import entity_version, offer_year_entity
from base.models.entity_version import EntityVersion, find_latest_version
from base.models.enums.organization_type import MAIN

SERVICE_COURSE = 'SERVICE_COURSE'


def find_from_offer_year(offer_year):
    return [entity_version.get_last_version(off_year_entity.entity)
            for off_year_entity in offer_year_entity.search(offer_year=offer_year).distinct('entity')]


def find_entity_version_according_academic_year(entity_versions, academic_year):
    """This function can be use after a prefetech_related"""
    return next((entity_vers for entity_vers in entity_versions
                 if entity_vers.start_date <= academic_year.end_date and
                 (entity_vers.end_date is None or entity_vers.end_date > academic_year.end_date)), None)


@attr.s(frozen=True, slots=True)
class MainEntityStructure:
    @attr.s(slots=True)
    class Node:
        entity_version = attr.ib(type=EntityVersion)
        parent = attr.ib(type=Optional['MainEntityStructure.Node'], default=None)
        direct_children = attr.ib(type=List['MainEntityStructure.Node'], factory=list)

        def faculty(self) -> 'MainEntityStructure.Node':
            if self.entity_version.is_faculty():
                return self
            if self.parent:
                return self.parent.faculty()
            return self

        def get_all_children(self) -> List['MainEntityStructure.Node']:
            return list(itertools.chain.from_iterable((child.get_all_children() for child in self.direct_children))) + \
                self.direct_children

    root = attr.ib(type='MainEntityStructure.Node')
    nodes = attr.ib(type=Dict[int, 'MainEntityStructure.Node'])

    def get_node(self, entity_id: int) -> Optional['MainEntityStructure.Node']:
        return self.nodes.get(entity_id)


def load_main_entity_structure(date: datetime.date) -> MainEntityStructure:
    all_current_entities_version = find_latest_version(date=date).of_main_organization  # type: Iterable[EntityVersion]

    nodes = {ev.entity.id: MainEntityStructure.Node(ev) for ev in all_current_entities_version}
    for ev in all_current_entities_version:
        if not ev.parent_id:
            continue
        nodes[ev.entity.id].parent = nodes[ev.parent_id]
        nodes[ev.parent_id].direct_children.append(nodes[ev.entity.id])

    root = next((value for key, value in nodes.items() if not value.parent))
    return MainEntityStructure(root, nodes)
