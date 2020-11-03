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

from base.ddd.utils import business_validator
from base.models.enums.education_group_types import TrainingType
from base.utils.constants import INFINITE_VALUE
from program_management.ddd.business_types import *
from program_management.ddd.domain import exception


#  TODO :: to remove
class Check2MEndDateGreaterOrEqualToItsFinalities(business_validator.BusinessValidator):
    def __init__(self, repository: 'ProgramTreeVersionRepository', tree_version: 'ProgramTreeVersion'):
        self.tree_version = tree_version
        self.repository = repository

    def validate(self, *args, **kwargs):
        finalities = self.tree_version.get_tree().get_all_finalities()
        if not finalities:
            return

        finality_with_greatest_end_date = self._get_finality_with_greatest_end_date(finalities)

        trees_2m = [
            tree for tree in self.tree_version.program_tree_repository.search_from_children(
                [self.tree_version.get_tree().root_node.entity_id],
            ) if tree.is_master_2m()
        ]
        tree_versions_2m = self.repository.search_versions_from_trees(trees_2m)
        for tree_version_2m in tree_versions_2m:
            root_end_year = tree_version_2m.end_year_of_existence or INFINITE_VALUE
            if (self.tree_version.end_year_of_existence or INFINITE_VALUE) > root_end_year:
                raise exception.Program2MEndDateShouldBeGreaterOrEqualThanItsFinalities(finality_with_greatest_end_date)

    def _get_finalities_where_end_date_gt_root_end_date(self, tree_2m: 'ProgramTree') -> List['Node']:
        inconsistent_finalities = []
        for finality in self.updated_tree.get_all_finalities():
            root_end_year = tree_2m.root_node.end_date or INFINITE_VALUE
            if (finality.end_year or INFINITE_VALUE) > root_end_year:
                inconsistent_finalities.append(finality)

        return inconsistent_finalities
