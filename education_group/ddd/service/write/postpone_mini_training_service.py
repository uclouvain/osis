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
from education_group.ddd.domain import exception
from education_group.ddd.domain.mini_training import MiniTrainingIdentity
from education_group.ddd.domain.service.calculate_end_postponement import CalculateEndPostponement
from education_group.ddd.service.write import copy_mini_training_service


@transaction.atomic()
def postpone_mini_training(postpone_cmd: command.PostponeMiniTrainingCommand) -> List['MiniTrainingIdentity']:
    identities_created = []

    # GIVEN
    from_year = postpone_cmd.postpone_from_year
    end_postponement_year = postpone_cmd.postpone_until_year

    # WHEN
    for year in range(from_year, end_postponement_year):
        try:
            identity_next_year = copy_mini_training_service.copy_mini_training_to_next_year(
                copy_cmd=command.CopyMiniTrainingToNextYearCommand(
                    acronym=postpone_cmd.acronym,
                    postpone_from_year=year
                )
            )

            # THEN
            identities_created.append(identity_next_year)
        except exception.CannotCopyMiniTrainingDueToEndDate:
            break

    return identities_created
