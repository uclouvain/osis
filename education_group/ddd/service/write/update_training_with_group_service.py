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

import attr
from django.db import transaction

from education_group.ddd import command
from education_group.ddd.business_types import *
from education_group.ddd.domain import training, group
from education_group.ddd.domain.service.calculate_end_postponement import CalculateEndPostponement
from education_group.ddd.repository import training as training_repository, group as group_repository
from education_group.ddd.service.write import update_training_service, update_group_service


@transaction.atomic()
def update_training_with_group(cmd: command.UpdateTrainingWithGroupCommand) -> List['TrainingIdentity']:
    training_identity = training.TrainingIdentity(acronym=cmd.abbreviated_title, year=cmd.year)
    training_domain_obj = training_repository.TrainingRepository.get(training_identity)
    group_identity = group.GroupIdentity(code=cmd.code, year=cmd.year)
    grp = group_repository.GroupRepository.get(group_identity)
    end_postponement_year = CalculateEndPostponement.calculate_year_of_end_postponement(
        training_domain_obj,
        training_repository.TrainingRepository,
        grp,
        group_repository.GroupRepository
    )

    new_cmd = attr.evolve(cmd, postpone_until_year=end_postponement_year)

    identities_of_modified_training = update_training_service.update_training(new_cmd)
    update_group_service.update_group(
        _convert_to_update_group_command(cmd, end_postponement_year)
    )
    return identities_of_modified_training


def _convert_to_update_group_command(
        cmd: command.UpdateTrainingWithGroupCommand,
        end_postponement_year: int) -> command.UpdateGroupCommand:
    return command.UpdateGroupCommand(
        code=cmd.code,
        year=cmd.year,
        abbreviated_title=cmd.abbreviated_title,
        title_fr=cmd.title_fr,
        title_en=cmd.title_en,
        credits=cmd.credits,
        constraint_type=cmd.constraint_type,
        min_constraint=cmd.min_constraint,
        max_constraint=cmd.max_constraint,
        management_entity_acronym=cmd.management_entity_acronym,
        teaching_campus_name=cmd.teaching_campus_name,
        organization_name=cmd.organization_name,
        remark_fr=cmd.remark_fr,
        remark_en=cmd.remark_en,
        postpone_until_year=end_postponement_year
    )
