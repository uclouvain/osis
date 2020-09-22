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
from program_management.ddd import command
from program_management.ddd.domain import program_tree_version
from program_management.ddd.repositories import program_tree_version as tree_version_repository


def calculate_version_max_end_year(cmd: command.GetVersionMaxEndYear) -> int:
    standard_tree_version_identity = program_tree_version.ProgramTreeVersionIdentity(
        offer_acronym=cmd.offer_acronym,
        year=cmd.year,
        version_name=program_tree_version.STANDARD,
        is_transition=False
    )

    tree_version = tree_version_repository.ProgramTreeVersionRepository.get(standard_tree_version_identity)
    return tree_version.end_year_of_existence
