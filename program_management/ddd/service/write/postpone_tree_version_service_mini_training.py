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

from education_group.ddd.domain.mini_training import MiniTrainingIdentity
from education_group.ddd.domain.training import TrainingIdentity
from education_group.ddd.repository.mini_training import MiniTrainingRepository
from education_group.ddd.repository.training import TrainingRepository
from program_management.ddd.command import PostponeProgramTreeVersionCommand, CopyTreeVersionToNextYearCommand
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.ddd.domain.service.calculate_end_postponement import CalculateEndPostponement
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.ddd.service.write import copy_program_version_service


@transaction.atomic()
def postpone_program_tree_version(
        postpone_cmd: 'PostponeProgramTreeVersionCommand'
) -> List['ProgramTreeVersionIdentity']:

    identities_created = []

    # GIVEN
    from_year = postpone_cmd.from_year
    end_postponement_year = CalculateEndPostponement.calculate_end_postponement_year_program_tree_version(
        identity=ProgramTreeVersionIdentity(
            offer_acronym=postpone_cmd.from_offer_acronym,
            version_name=postpone_cmd.from_version_name,
            year=postpone_cmd.from_year,
            is_transition=postpone_cmd.from_is_transition,
        ),
        repository=ProgramTreeVersionRepository()
    )

    # WHEN
    while from_year < end_postponement_year:
        cmd_copy_from = CopyTreeVersionToNextYearCommand(
            from_offer_acronym=postpone_cmd.from_offer_acronym,
            from_offer_code=postpone_cmd.from_code,
            from_year=from_year,
            from_version_name=postpone_cmd.from_version_name,
            from_is_transition=postpone_cmd.from_is_transition,
        )
        identity_next_year = copy_program_version_service.copy_tree_version_to_next_year(cmd_copy_from)

        # THEN
        identities_created.append(identity_next_year)
        from_year += 1

    return identities_created
