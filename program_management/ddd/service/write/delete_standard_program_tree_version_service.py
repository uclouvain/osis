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
import itertools
from typing import List

from django.db import transaction

from program_management.ddd import command
from program_management.ddd.business_types import *
from program_management.ddd.domain import exception, program_tree_version
from program_management.ddd.repositories import program_tree_version as program_tree_version_repository


@transaction.atomic()
def delete_standard_program_tree_version(
        delete_command: command.DeleteProgramTreeVersionCommand) -> List['ProgramTreeVersionIdentity']:
    from_year = delete_command.from_year

    deleted_program_tree_versions = []
    for year in itertools.count(from_year):
        program_tree_version_identity_to_delete = program_tree_version.ProgramTreeVersionIdentity(
            offer_acronym=delete_command.offer_acronym,
            year=year,
            version_name=delete_command.version_name,
            is_transition=delete_command.is_transition
        )
        try:
            program_tree_version_repository.ProgramTreeVersionRepository.delete(program_tree_version_identity_to_delete)
            deleted_program_tree_versions.append(program_tree_version_identity_to_delete)
        except exception.ProgramTreeVersionNotFoundException:
            break

    return deleted_program_tree_versions
