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
from typing import List

from django.db import transaction

from base.models.enums.active_status import ActiveStatusEnum
from base.models.enums.schedule_type import ScheduleTypeEnum
from education_group.ddd import command
from education_group.ddd.business_types import *
from education_group.ddd.domain import group, mini_training
from education_group.ddd.domain._campus import Campus
from education_group.ddd.domain._entity import Entity
from education_group.ddd.domain._titles import Titles
from education_group.ddd.domain.service.calculate_end_postponement import CalculateEndPostponement
from education_group.ddd.repository import mini_training as mini_training_repository, group as group_repository
from education_group.ddd.service.write import postpone_mini_training_service


@transaction.atomic()
def update_mini_training(cmd: command.UpdateMiniTrainingCommand) -> List['MiniTrainingIdentity']:
    mini_training_identity = mini_training.MiniTrainingIdentity(acronym=cmd.abbreviated_title, year=cmd.year)
    group_identity = group.GroupIdentity(code=cmd.code, year=cmd.year)

    postpone_until_year = CalculateEndPostponement.calculate_year_of_postponement_for_mini_training(
        mini_training_identity,
        group_identity,
        mini_training_repository.MiniTrainingRepository,
        group_repository.GroupRepository
    )

    mini_training_domain_obj = mini_training_repository.MiniTrainingRepository.get(mini_training_identity)

    mini_training_domain_obj.update(convert_command_to_update_mini_training_data(cmd))
    mini_training_repository.MiniTrainingRepository.update(mini_training_domain_obj)

    result = postpone_mini_training_service.postpone_mini_training(
        command.PostponeMiniTrainingCommand(
            acronym=cmd.abbreviated_title,
            postpone_from_year=cmd.year,
            postpone_until_year=postpone_until_year
        )
    )

    return [mini_training_identity] + result


def convert_command_to_update_mini_training_data(
        cmd: command.UpdateMiniTrainingCommand) -> 'mini_training.UpdateMiniTrainingData':
    return mini_training.UpdateMiniTrainingData(
        credits=cmd.credits,
        titles=Titles(
            title_fr=cmd.title_fr,
            title_en=cmd.title_en,
        ),
        status=ActiveStatusEnum[cmd.status],
        keywords=cmd.keywords,
        management_entity=Entity(acronym=cmd.management_entity_acronym),
        end_year=cmd.end_year,
        teaching_campus=Campus(name=cmd.teaching_campus_name, university_name=cmd.teaching_campus_organization_name),
        schedule_type=ScheduleTypeEnum[cmd.schedule_type],
    )
