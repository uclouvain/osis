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

from education_group.ddd.repository.mini_training import MiniTrainingRepository
from education_group.ddd.repository.training import TrainingRepository
from program_management.ddd import command
from program_management.ddd.domain.program_tree import ProgramTreeIdentity
from program_management.ddd.domain.service.calculate_end_postponement import CalculateEndPostponement


def calculate_program_tree_end_postponement(
        cmd: command.GetEndPostponementYearCommand
) -> int:
    return CalculateEndPostponement().calculate_program_tree_end_postponement(
        identity=ProgramTreeIdentity(cmd.code, cmd.year),
        training_repository=TrainingRepository(),
        mini_training_repository=MiniTrainingRepository()
    )
