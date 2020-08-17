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

from program_management.ddd.command import PostponeProgramTreeVersionCommand, CreateProgramTreeVersionCommand, \
    DuplicateProgramTree, PostponeProgramTreeCommand
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionBuilder, ProgramTreeVersionIdentity, \
    STANDARD
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.ddd.service.write import postpone_tree_version_service, duplicate_program_tree_service, \
    postpone_program_tree_service


def create_program_tree_version(
        command: 'CreateProgramTreeVersionCommand',
) -> ProgramTreeVersionIdentity:

    # GIVEN
    identity_standard = ProgramTreeVersionIdentity(
        offer_acronym=command.offer_acronym,
        year=command.year,
        version_name=STANDARD,
        is_transition=False
    )
    program_tree_version_standard = ProgramTreeVersionRepository().get(entity_id=identity_standard)

    # WHEN
    new_program_tree_identity = duplicate_program_tree_service.duplicate_program_tree(
        DuplicateProgramTree(
            from_root_code=program_tree_version_standard.program_tree_identity.code,
            from_root_year=program_tree_version_standard.program_tree_identity.year,
        )
    )
    new_program_tree_version = ProgramTreeVersionBuilder().create_from_standard_version(
        program_tree_version_standard,
        new_program_tree_identity,
        command,
    )

    # THEN
    identity = ProgramTreeVersionRepository.create(
        program_tree_version=new_program_tree_version,
    )

    return identity


def create_and_postpone_from_past_version(command: 'CreateProgramTreeVersionCommand') -> List[ProgramTreeVersionIdentity]:
    # GIVEN
    creation_year = command.year
    identity_to_create = ProgramTreeVersionIdentity(
        offer_acronym=command.offer_acronym,
        year=creation_year,
        version_name=command.version_name,
        is_transition=command.is_transition,
    )
    last_existing_tree_version = ProgramTreeVersionRepository().get_last_in_past(identity_to_create)

    postpone_program_tree_service.postpone_program_tree(
        PostponeProgramTreeCommand(
            from_code=last_existing_tree_version.program_tree_identity.code,
            from_year=last_existing_tree_version.program_tree_identity.year,
            offer_acronym=identity_to_create.offer_acronym,
            until_year=int(command.end_year) if command.end_year else None
        )
    )

    created_identities_from_past = postpone_tree_version_service.postpone_program_tree_version(
        PostponeProgramTreeVersionCommand(
            from_offer_acronym=last_existing_tree_version.entity_id.offer_acronym,
            from_version_name=last_existing_tree_version.entity_id.version_name,
            from_year=last_existing_tree_version.entity_id.year,
            from_is_transition=last_existing_tree_version.entity_id.is_transition,
            until_year=int(command.end_year) if command.end_year else None
        )
    )
    return created_identities_from_past
