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
from typing import List

from django.db import transaction

from base.models.enums.education_group_types import MiniTrainingType, TrainingType
from education_group.ddd import command
from education_group.ddd.domain import exception
from education_group.ddd.domain.group import GroupIdentity
from education_group.ddd.domain.service.identity_search import TrainingIdentitySearch, MiniTrainingIdentitySearch
from education_group.ddd.repository.mini_training import MiniTrainingRepository
from education_group.ddd.repository.training import TrainingRepository
from education_group.ddd.service.read import get_group_service
from education_group.ddd.service.write import copy_group_service
from osis_common.ddd.interface import BusinessException
from program_management.ddd.domain.service.calculate_end_postponement import CalculateEndPostponement


@transaction.atomic()
def postpone_group(postpone_cmd: command.PostponeGroupCommand) -> List['GroupIdentity']:
    identities_created = []

    from_year = postpone_cmd.postpone_from_year

    cmd_get = command.GetGroupCommand(code=postpone_cmd.code, year=from_year)
    group = get_group_service.get_group(cmd_get)

    if group.type.name in MiniTrainingType.get_names():
        identity = MiniTrainingIdentitySearch.get_from_group_identity(group.entity_id)
        repository = MiniTrainingRepository()
    elif group.type.name in TrainingType.get_names():
        identity = TrainingIdentitySearch.get_from_group_identity(group.entity_id)
        repository = TrainingRepository()
    else:
        raise BusinessException("Cannot postpone group other type than Mini-Training/Training")

    end_postponement_year = CalculateEndPostponement.calculate_end_postponement_year(
        identity=identity,
        repository=repository,
    )
    for year in range(from_year, end_postponement_year):
        try:
            identity_next_year = copy_group_service.copy_group(
                cmd=command.CopyGroupCommand(from_code=postpone_cmd.code, from_year=year)
            )
            identities_created.append(identity_next_year)
        except exception.CannotCopyGroupDueToEndDate:
            break

    return identities_created
