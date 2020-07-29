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

from education_group.ddd.service.write import delete_training_service, delete_group_service
from program_management.ddd import command
from program_management.ddd.service.write import delete_standard_program_tree_version_service, \
    delete_standard_program_tree_service
from education_group.ddd import command as education_group_command
from education_group.ddd.business_types import *


@transaction.atomic()
def delete_training_with_program_tree(
        delete_command: command.DeleteTrainingWithProgramTreeCommand) -> List['TrainingIdentity']:
    delete_program_tree_version_command = command.DeleteProgramTreeVersionCommand(
        offer_acronym=delete_command.offer_acronym,
        version_name=delete_command.version_name,
        is_transition=delete_command.is_transition,
        from_year=delete_command.from_year
    )
    delete_standard_program_tree_version_service.delete_standard_program_tree_version(
        delete_program_tree_version_command
    )

    delete_program_tree_command = command.DeleteStandardProgramTreeCommand(
        code=delete_command.code,
        from_year=delete_command.from_year
    )
    delete_standard_program_tree_service.delete_standard_program_tree(delete_program_tree_command)

    delete_training_command = education_group_command.DeleteTrainingCommand(
        acronym=delete_command.offer_acronym,
        from_year=delete_command.from_year
    )
    training_identities = delete_training_service.delete_training(delete_training_command)

    delete_group_command = education_group_command.DeleteGroupCommand(
        code=delete_command.code,
        from_year=delete_command.from_year
    )
    delete_group_service.delete_group(delete_group_command)

    return training_identities
