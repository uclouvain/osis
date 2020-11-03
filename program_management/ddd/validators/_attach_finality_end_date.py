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
import sys
from typing import List, Set

from base.ddd.utils import business_validator
from base.models.enums.education_group_types import TrainingType
from base.utils.constants import INFINITE_VALUE
from program_management.ddd.business_types import *
from program_management.ddd.domain.exception import CannotAttachFinalitiesWithGreaterEndDateThanProgram2M, \
    Program2MEndDateShouldBeGreaterOrEqualThanItsFinalities


#  TODO : to rename into CheckEndDateBetweenFinalitiesAndMasters2M + rename file
class AttachFinalityEndDateValidator(business_validator.BusinessValidator):
    """
    In context of 2M, when we add a finality [or group which contains finality], we must ensure that
    the end date of all 2M is greater or equals of all finalities.
    """

    def __init__(
            self,
            updated_tree_version: 'ProgramTreeVersion',
            # FIXME :: The kwarg below is only useful because the validation is performed BEFORE the "Paste" action.
            # FIXME :: To remove this param, we need to call this Validator AFTER the action "paste" is Done.
            # FIXME :: (like the "update program tree version" action that uses this validator too)
            trees_2m: List['ProgramTree'] = None
    ):
        super(AttachFinalityEndDateValidator, self).__init__()
        if trees_2m:
            assert_msg = "To use correctly this validator, make sure the ProgramTree root is of type 2M"
            for tree_2m in trees_2m:
                assert tree_2m.root_node.node_type in TrainingType.root_master_2m_types_enum(), assert_msg
        self.updated_tree_version = updated_tree_version
        self.updated_tree = updated_tree_version.get_tree()
        self.program_tree_repository = updated_tree_version.program_tree_repository
        self.trees_2m = trees_2m

    def validate(self):
        if self.updated_tree.root_node.is_finality() or self.updated_tree.get_all_finalities():
            if self.updated_tree.root_node.is_master_2m():
                self._check_master_2M_end_year_greater_or_equal_to_its_finalities()
            else:
                self._check_finalities_end_year_greater_or_equal_to_their_masters_2M()

    def _check_master_2M_end_year_greater_or_equal_to_its_finalities(self):
        inconsistent_finalities = self._get_finalities_where_end_year_gt_root_end_year(self.updated_tree)
        if inconsistent_finalities:
            #  TODO :: to rename into Program2MEndDateLowerThanItsFinalities
            raise Program2MEndDateShouldBeGreaterOrEqualThanItsFinalities(self.updated_tree.root_node)

    def _check_finalities_end_year_greater_or_equal_to_their_masters_2M(self):
        trees_2m = self._search_master_2m_trees()
        for tree_2m in trees_2m:
            inconsistent_finalities = self._get_finalities_where_end_year_gt_root_end_year(tree_2m)
            if inconsistent_finalities:
                #  TODO :: to rename into FinalitiesEndDateGreaterThanTheirMasters2M
                raise CannotAttachFinalitiesWithGreaterEndDateThanProgram2M(
                    tree_2m.root_node,
                    inconsistent_finalities
                )

    def _get_finalities_where_end_year_gt_root_end_year(self, tree_2m: 'ProgramTree') -> List['Node']:
        inconsistent_finalities = []
        for finality in self.updated_tree.get_all_finalities():
            root_end_year = tree_2m.root_node.end_year or INFINITE_VALUE
            if (finality.end_year or INFINITE_VALUE) > root_end_year:
                inconsistent_finalities.append(finality)

        return inconsistent_finalities

    def _search_master_2m_trees(self) -> List['ProgramTree']:
        if self.trees_2m:
            return self.trees_2m
        root_identity = self.updated_tree.root_node.entity_id
        trees_2m = [
            tree for tree in self.program_tree_repository.search_from_children([root_identity])
            if tree.is_master_2m()
        ]
        return trees_2m
