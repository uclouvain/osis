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
from django.db import transaction

from program_management.ddd import command
from program_management.ddd.domain.program_tree import ProgramTreeIdentity
from program_management.ddd.repositories.program_tree import ProgramTreeRepository
from program_management.ddd.service.write import delete_node_service
from program_management.ddd.validators.validators_by_business_action import DeleteProgramTreeValidatorList


@transaction.atomic()
def delete_program_tree(cmd: command.DeleteProgramTreeCommand) -> ProgramTreeIdentity:
    program_tree_id = ProgramTreeIdentity(code=cmd.code, year=cmd.year)
    program_tree = ProgramTreeRepository.get(program_tree_id)

    DeleteProgramTreeValidatorList(program_tree).validate()

    ProgramTreeRepository.delete(
        program_tree_id,

        # Service Dependancy injection
        delete_node_service=delete_node_service.delete_node
    )
    return program_tree_id
