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
from django.db import transaction

from education_group.ddd.command import UpdateGroupCommand
from education_group.ddd.service.write import update_group_service
from program_management.ddd.business_types import *
from program_management.ddd.command import UpdateProgramTreeVersionCommand, \
    UpdateMiniTrainingVersionCommand, DeleteSpecificVersionCommand
from program_management.ddd.domain.service.calculate_end_postponement import CalculateEndPostponement
from program_management.ddd.domain.service.identity_search import GroupIdentitySearch
from program_management.ddd.service.write import update_program_tree_version_service, delete_specific_version_service


@transaction.atomic
def update_mini_training_version(
        command: 'UpdateMiniTrainingVersionCommand',
) -> 'ProgramTreeVersionIdentity':

    tree_version_identity = update_program_tree_version_service.update_program_tree_version(
        __convert_to_update_tree_version_command(command)
    )

    update_group_service.update_group(
        __convert_to_update_group_command(command, tree_version_identity)
    )

    return tree_version_identity


def __convert_to_update_group_command(
        cmd: 'UpdateMiniTrainingVersionCommand',
        tree_version_identity: 'ProgramTreeVersionIdentity'
) -> 'UpdateGroupCommand':
    group_identity = GroupIdentitySearch().get_from_tree_version_identity(tree_version_identity)
    return UpdateGroupCommand(
        code=group_identity.code,
        year=cmd.year,
        abbreviated_title=cmd.offer_acronym,
        title_fr=cmd.title_fr,
        title_en=cmd.title_en,
        credits=cmd.credits,
        constraint_type=cmd.constraint_type,
        min_constraint=cmd.min_constraint,
        max_constraint=cmd.max_constraint,
        management_entity_acronym=cmd.management_entity_acronym,
        teaching_campus_name=cmd.teaching_campus_name,
        organization_name=cmd.teaching_campus_organization_name,
        remark_fr=cmd.remark_fr,
        remark_en=cmd.remark_en,
        end_year=cmd.end_year,
    )


def __convert_to_update_tree_version_command(command: 'UpdateMiniTrainingVersionCommand'):
    return UpdateProgramTreeVersionCommand(
        end_year=command.end_year,
        offer_acronym=command.offer_acronym,
        version_name=command.version_name,
        year=command.year,
        is_transition=command.is_transition,
        title_en=command.title_en,
        title_fr=command.title_fr,
    )


def __call_delete_service(program_tree_version: 'ProgramTreeVersion', end_year_updated: int):
    identity = program_tree_version.entity_identity

    postponement_limit = CalculateEndPostponement.calculate_end_postponement_limit()

    end_year = program_tree_version.end_year_of_existence or postponement_limit
    end_year_updated = end_year_updated or postponement_limit

    if end_year > end_year_updated:
        for year_to_delete in range(end_year_updated, program_tree_version.end_year_of_existence):
            delete_specific_version_service.delete_specific_version(
                DeleteSpecificVersionCommand(
                    acronym=identity.offer_acronym,
                    year=year_to_delete,
                    version_name=identity.version_name,
                    is_transition=identity.is_transition,
                )
            )
