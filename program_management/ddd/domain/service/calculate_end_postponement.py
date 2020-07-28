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
from base.models import academic_year
from education_group.ddd.repository.group import GroupRepository
from osis_common.ddd import interface
from education_group.ddd.business_types import *
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.ddd.domain.service.identity_search import GroupIdentitySearch


class CalculateEndPostponement(interface.DomainService):

    @classmethod
    def calculate_program_tree_end_postponement_year(
            cls,
            training_identity: 'TrainingIdentity',
            training_repository: 'TrainingRepository'
    ) -> int:
        default_years_to_postpone = 5
        current_year = academic_year.starting_academic_year().year
        training = training_repository.get(training_identity)
        if training.end_year:
            default_years_to_postpone = training.end_year - training.year
        return current_year + default_years_to_postpone

    @classmethod
    def calculate_tree_version_end_postponement_year(  # TODO :: review : is this at the correct place?
            cls,
            tree_version_identity: 'ProgramTreeVersionIdentity',
            group_repository: 'GroupRepository',
    ) -> int:
        default_years_to_postpone = 5
        group = group_repository.get(GroupIdentitySearch().get_from_tree_version_identity(tree_version_identity))
        if group.end_year:
            default_years_to_postpone = group.end_year - group.year
        return academic_year.starting_academic_year().year + default_years_to_postpone
