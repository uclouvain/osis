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
import copy

import attr

from base.models.enums.active_status import ActiveStatusEnum
from base.models.enums.constraint_type import ConstraintTypeEnum
from base.models.enums.education_group_types import EducationGroupTypesEnum, MiniTrainingType
from base.models.enums.schedule_type import ScheduleTypeEnum
from education_group.ddd import command
from education_group.ddd.domain._campus import Campus
from education_group.ddd.domain._content_constraint import ContentConstraint
from education_group.ddd.domain._entity import Entity
from education_group.ddd.domain._remark import Remark
from education_group.ddd.domain._titles import Titles
from osis_common.ddd import interface


class MiniTrainingBuilder:
    @classmethod
    def build_from_create_cmd(self, cmd: command.CreateOrphanMiniTrainingCommand):
        mini_training_id = MiniTrainingIdentity(code=cmd.code, year=cmd.year)
        titles = Titles(title_fr=cmd.title_fr, title_en=cmd.title_en)
        content_constraint = ContentConstraint(
            type=ConstraintTypeEnum[cmd.constraint_type] if cmd.constraint_type else None,
            minimum=cmd.min_constraint,
            maximum=cmd.max_constraint
        )
        management_entity = Entity(acronym=cmd.management_entity_acronym)
        teaching_campus = Campus(
            name=cmd.teaching_campus_name,
            university_name=cmd.organization_name,
        )
        remark = Remark(text_fr=cmd.remark_fr, text_en=cmd.remark_en)

        return MiniTraining(
            entity_identity=mini_training_id,
            type=MiniTrainingType[cmd.type],
            abbreviated_title=cmd.abbreviated_title,
            titles=titles,
            status=ActiveStatusEnum[cmd.status],
            schedule_type=ScheduleTypeEnum[cmd.schedule_type],
            credits=cmd.credits,
            content_constraint=content_constraint,
            management_entity=management_entity,
            teaching_campus=teaching_campus,
            remark=remark,
            start_year=cmd.start_year,
            unannualized_identity=None,
            end_year=cmd.end_year
        )

    @classmethod
    def build_next_year_mini_training(cls, from_mini_training: 'MiniTraining'):
        mini_training = copy.deepcopy(from_mini_training)
        mini_training.entity_id = MiniTrainingIdentity(code=from_mini_training.code, year=from_mini_training.year + 1)
        return mini_training


builder = MiniTrainingBuilder()


@attr.s(frozen=True, slots=True)
class MiniTrainingIdentity(interface.EntityIdentity):
    code = attr.ib(type=str, converter=lambda code: code.upper())
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class MiniTrainingUnannualizedIdentity(interface.ValueObject):
    """
    This ID is necessary to find a Mini Training through years because code can be different through years
    """
    uuid = attr.ib(type=int)


class MiniTraining(interface.RootEntity):
    def __init__(
            self,
            entity_identity: 'MiniTrainingIdentity',
            type: EducationGroupTypesEnum,
            abbreviated_title: str,
            titles: Titles,
            status: ActiveStatusEnum,
            schedule_type: ScheduleTypeEnum,
            credits: int,
            content_constraint: ContentConstraint,
            management_entity: Entity,
            teaching_campus: Campus,
            remark: Remark,
            start_year: int,
            unannualized_identity: 'MiniTrainingUnannualizedIdentity' = None,
            end_year: int = None,
    ):
        super().__init__(entity_id=entity_identity)
        self.entity_id = entity_identity
        self.type = type
        self.abbreviated_title = abbreviated_title.upper()
        self.titles = titles
        self.status = status
        self.schedule_type = schedule_type
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
