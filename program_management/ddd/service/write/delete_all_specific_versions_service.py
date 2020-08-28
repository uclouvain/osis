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

from program_management.ddd import command
from program_management.ddd.business_types import *
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.ddd.service.write import delete_program_tree_service, delete_specific_version_service


@transaction.atomic()
def delete_all_program_tree_versions(
        cmd: command.DeleteAllSpecificVersionCommand
) -> List['ProgramTreeVersionIdentity']:

    tree_versions_to_delete = ProgramTreeVersionRepository().search(
        version_name=cmd.version_name,
        acronym=cmd.acronym,
        is_transition=cmd.is_transition,
    )

    tree_versions_identities = []
    for tree_version in tree_versions_to_delete:
        _call_delete_program_tree_service(tree_version)
        deleted_tree_version_identity = _call_delete_specific_version_service(tree_version)
        tree_versions_identities.append(deleted_tree_version_identity)

    return tree_versions_identities


def _call_delete_specific_version_service(tree_version: 'ProgramTreeVersion') -> 'ProgramTreeVersionIdentity':
    return delete_specific_version_service.delete_specific_version(
        command.DeleteSpecificVersionCommand(
            acronym=tree_version.entity_identity.acronym,
            year=tree_version.entity_identity.year,
            version_name=tree_version.entity_identity.version_name,
            is_transition=tree_version.entity_identity.is_transition,
        )
    )


def _call_delete_program_tree_service(tree_version: 'ProgramTreeVersion') -> List['ProgramTreeIdentity']:
    cmd_delete_program_tree = command.DeleteProgramTreeCommand(
        code=tree_version.program_tree_identity.code,
        year=tree_version.program_tree_identity.year,
    )
    return delete_program_tree_service.delete_program_tree(cmd_delete_program_tree)
