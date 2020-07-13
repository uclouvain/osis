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

from education_group.ddd import command
from education_group.ddd.business_types import *
from education_group.ddd.service.write import copy_training_service


def postpone_training(postpone_cmd: command.PostponeTrainingCommand) -> List['TrainingIdentity']:
    identities_created = []

    from_year = postpone_cmd.postpone_from_year
    while from_year < postpone_cmd.postpone_until_year:
        # GIVEN
        cmd_copy_from = command.CopyTrainingToNextYearCommand(acronym=postpone_cmd.acronym, postpone_from_year=from_year)

        # WHEN
        identity_next_year = copy_training_service.copy_training_to_next_year(cmd_copy_from)

        # THEN
        identities_created.append(identity_next_year)
        from_year += 1

    return identities_created
