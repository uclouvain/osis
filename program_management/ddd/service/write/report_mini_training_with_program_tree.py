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

from education_group.ddd import command
from education_group.ddd.business_types import *
from education_group.ddd.domain.service.calculate_end_postponement import CalculateEndPostponement
from education_group.ddd.service.write import postpone_group_service, \
    postpone_mini_training_service
from program_management.ddd.command import PostponeProgramTreeCommand, PostponeProgramTreeVersionCommand
from program_management.ddd.service.write import postpone_program_tree_service, postpone_tree_version_service


@transaction.atomic()
def report_mini_training_with_program_tree(
        report_cmd: command.PostponeMiniTrainingWithProgramTreeCommand
) -> List['MiniTrainingIdentity']:
    mini_training_identities = postpone_mini_training_service.postpone_mini_training(
        command.PostponeMiniTrainingCommand(
            acronym=report_cmd.abbreviated_title,
            postpone_from_year=report_cmd.from_year,
            postpone_until_year=CalculateEndPostponement.calculate_max_year_of_end_postponement()
        )
    )

    postpone_group_service.postpone_group(
        command.PostponeGroupCommand(
            code=report_cmd.code,
            postpone_from_year=report_cmd.from_year,
            postpone_until_year=CalculateEndPostponement.calculate_max_year_of_end_postponement()
        )
    )

    postpone_program_tree_service.postpone_program_tree(
        PostponeProgramTreeCommand(
            from_code=report_cmd.code,
            from_year=report_cmd.from_year,
            offer_acronym=report_cmd.abbreviated_title,
            until_year=CalculateEndPostponement.calculate_max_year_of_end_postponement()
        )
    )

    postpone_tree_version_service.postpone_program_tree_version(
        PostponeProgramTreeVersionCommand(
            from_offer_acronym=report_cmd.abbreviated_title,
            from_version_name="",
            from_year=report_cmd.from_year,
            from_is_transition=False,
            until_year=CalculateEndPostponement.calculate_max_year_of_end_postponement()
        )
    )

    return mini_training_identities
