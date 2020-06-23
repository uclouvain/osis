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
from typing import Set

from base.models.enums.education_group_categories import Categories
from base.models.enums.education_group_types import GroupType, TrainingType, MiniTrainingType
from program_management.ddd import command
from program_management.ddd.repositories import load_authorized_relationship, load_tree
from program_management.ddd.repositories.program_tree import ProgramTreeRepository
from program_management.ddd.validators._authorized_relationship import PasteAuthorizedRelationshipValidator


def get_allowed_child_types(cmd: command.GetAllowedChildTypeCommand) -> Set:
    if cmd.category == Categories.TRAINING:
        allowed_child_types = TrainingType
    elif cmd.category == Categories.MINI_TRAINING:
        allowed_child_types = MiniTrainingType
    else:
        allowed_child_types = GroupType

    if cmd.path_to_paste:
        pass
        # tree_id =
        # tree = ProgramTreeRepository.get()
        # authorized_relationship = load_authorized_relationship.load()
        # PasteAuthorizedRelationshipValidator()

    return {child_type for child_type in allowed_child_types}
