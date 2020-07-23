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

from program_management.ddd.command import PostponeProgramTreeVersionCommand, CreateProgramTreeVersionCommand
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionBuilder, ProgramTreeVersionIdentity, \
    STANDARD
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository


def create_program_tree_version(
        command: 'CreateProgramTreeVersionCommand',
        identity_trough_year: int = None,
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
    new_program_tree_version = ProgramTreeVersionBuilder().build_from(
        program_tree_version_standard,
        command,
        identity_trough_year=identity_trough_year,
    )

    # THEN
    identity = ProgramTreeVersionRepository.create(program_tree_version=new_program_tree_version)

    return identity


def postpone_program_tree_version(command: 'PostponeProgramTreeVersionCommand') -> List[ProgramTreeVersionIdentity]:
    # GIVEN
    identity = ProgramTreeVersionIdentity(
        offer_acronym=command.from_offer_acronym,
        year=command.from_year,
        version_name=command.from_version_name,
        is_transition=command.from_is_transition,
    )
    existing_program_tree_version = ProgramTreeVersionRepository().get(entity_id=identity)

    identities_created = []

    # WHEN
    from_year = existing_program_tree_version.entity_id.year
    while from_year < command.end_postponement:
        from_year += 1

        # THEN
        command = CreateProgramTreeVersionCommand(
            end_postponement=command.end_postponement,
            offer_acronym=existing_program_tree_version.entity_id.offer_acronym,
            version_name=existing_program_tree_version.entity_id.version_name,
            year=existing_program_tree_version.entity_id.year,
            is_transition=existing_program_tree_version.entity_id.is_transition,
            title_en=existing_program_tree_version.title_en,
            title_fr=existing_program_tree_version.title_fr,
        )
        identities_created.append(
            create_program_tree_version(
                command,
                identity_trough_year=existing_program_tree_version.identity_trough_year,
            )
        )

    return identities_created


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

    # WHEN
    created_identities_in_past = postpone_program_tree_version(
        PostponeProgramTreeVersionCommand(
            end_postponement=creation_year,
            from_offer_acronym=last_existing_tree_version.entity_id.offer_acronym,
            from_version_name=last_existing_tree_version.entity_id.version_name,
            from_year=last_existing_tree_version.entity_id.year,
            from_is_transition=last_existing_tree_version.entity_id.is_transition,
        )
    )

    # THEN
    created_identity = create_program_tree_version(command)

    created_identities_in_future = postpone_program_tree_version(
        PostponeProgramTreeVersionCommand(
            end_postponement=command.end_postponement,
            from_offer_acronym=created_identity.offer_acronym,
            from_version_name=created_identity.version_name,
            from_year=created_identity.year,
            from_is_transition=created_identity.is_transition,
        )
    )

    return created_identities_in_past + [created_identity] + created_identities_in_future
