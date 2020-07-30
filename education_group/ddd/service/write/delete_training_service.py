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

from education_group.ddd import command
from education_group.ddd.business_types import *
from education_group.ddd.domain import training, exception
from education_group.ddd.repository import training as training_repository
from education_group.ddd.validators.validators_by_business_action import DeleteTrainingValidatorList


#  FIXME split in delete training and delete multiple trainings
def delete_training(delete_command: command.DeleteTrainingCommand) -> List['TrainingIdentity']:
    from_year = delete_command.from_year

    deleted_trainings = []
    for year in itertools.count(from_year):
        training_identity_to_delete = training.TrainingIdentity(acronym=delete_command.acronym, year=year)
        try:
            training_obj = training_repository.TrainingRepository.get(training_identity_to_delete)
            DeleteTrainingValidatorList(training_obj).validate()

            training_repository.TrainingRepository.delete(training_identity_to_delete)
            deleted_trainings.append(training_identity_to_delete)
        except exception.TrainingNotFoundException:
            break

    return deleted_trainings
