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

from education_group.ddd import command
from education_group.ddd.business_types import *
from education_group.ddd.domain import training, group
from education_group.ddd.domain.service import calculate_end_postponement
from education_group.ddd.repository import training as training_repository, group as group_repository
from education_group.ddd.service.write import update_training_service, update_group_service
from program_management.ddd.command import PostponeProgramTreeVersionCommand, \
    PostponeProgramTreeCommand
from program_management.ddd.service.write import postpone_tree_version_service, \
    postpone_program_tree_service


@transaction.atomic()
def update_and_report_training_with_program_tree(
        update_command: command.UpdateTrainingCommand
) -> List['TrainingIdentity']:
    postpone_until_year = calculate_end_postponement.CalculateEndPostponement.calculate_year_of_postponement(
        training.TrainingIdentity(acronym=update_command.abbreviated_title, year=update_command.year),
        group.GroupIdentity(code=update_command.code, year=update_command.year),
        training_repository.TrainingRepository,
        group_repository.GroupRepository
    )

    training_identities = update_training_service.update_training(update_command)

    update_group_service.update_group(_convert_to_update_group_command(update_command))

    postpone_program_tree_service.postpone_program_tree(
        PostponeProgramTreeCommand(
            from_code=update_command.code,
            from_year=update_command.year,
            offer_acronym=update_command.abbreviated_title,
            until_year=postpone_until_year
        )
    )

    postpone_tree_version_service.postpone_program_tree_version(
        PostponeProgramTreeVersionCommand(
            from_offer_acronym=update_command.abbreviated_title,
            from_version_name="",
            from_year=update_command.year,
            from_is_transition=False,
            until_year=postpone_until_year
        )
    )

    return training_identities


def _convert_to_update_group_command(training_cmd: command.UpdateTrainingCommand) -> command.UpdateGroupCommand:
    return command.UpdateGroupCommand(
        code=training_cmd.code,
        year=training_cmd.year,
        abbreviated_title=training_cmd.abbreviated_title,
        title_fr=training_cmd.title_fr,
        title_en=training_cmd.title_en,
        credits=training_cmd.credits,
        constraint_type=training_cmd.constraint_type,
        min_constraint=training_cmd.min_constraint,
        max_constraint=training_cmd.max_constraint,
        management_entity_acronym=training_cmd.management_entity_acronym,
        teaching_campus_name=training_cmd.teaching_campus_name,
        organization_name=training_cmd.teaching_campus_organization_name,
        remark_fr=training_cmd.remark_fr,
        remark_en=training_cmd.remark_en,
        end_year=training_cmd.end_year
    )
