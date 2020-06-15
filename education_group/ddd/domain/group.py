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
from base.models.enums.education_group_types import GroupType
from education_group.ddd.domain._campus import Campus
from education_group.ddd.domain._content_constraint import ContentConstraint
from education_group.ddd.domain._entity import Entity
from education_group.ddd.domain._remark import Remark
from education_group.ddd.domain._titles import Titles
from osis_common.ddd import interface


class GroupIdentity(interface.EntityIdentity):
    def __init__(self, code: str, year: int):
        self.code = code
        self.year = year

    def __hash__(self):
        return hash(self.code + str(self.year))

    def __eq__(self, other):
        return self.code == other.code and self.year == other.year


class GroupUnannualizedIdentity(interface.EntityIdentity):
    """
    This ID is necessary to find a GROUP through years because code can be different accros years
    """
    def __init__(self, uuid: str):
        self.uuid = uuid

    def __hash__(self):
        return hash(self.uuid)

    def __eq__(self, other):
        return self.uuid == other.uuid


class Group(interface.RootEntity):
    def __init__(
        self,
        entity_identity: 'GroupIdentity',
        type: GroupType,
        abbreviated_title: str,
        titles: Titles,
        credits: int,
        content_constraint: ContentConstraint,
        management_entity: Entity,
        teaching_campus: Campus,
        remark: Remark,
        start_year: int,
        unannualized_identity: 'GroupUnannualizedIdentity' = None,
        end_year: int = None,
    ):
        super(Group, self).__init__(entity_id=entity_identity)
        self.entity_id = entity_identity
        self.type = type
        self.abbreviated_title = abbreviated_title
        self.titles = titles
        self.credits = credits
        self.content_constraint = content_constraint
        self.management_entity = management_entity
        self.teaching_campus = teaching_campus
        self.remark = remark
        self.start_year = start_year
        self.unannualized_identity = unannualized_identity
        self.end_year = end_year

    @property
    def code(self) -> str:
        return self.entity_id.code

    @property
    def year(self) -> int:
        return self.entity_id.year
