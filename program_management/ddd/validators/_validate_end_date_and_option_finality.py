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
import osis_common.ddd.interface
from base.ddd.utils import business_validator
from program_management.ddd.business_types import *
from program_management.ddd.domain import program_tree as program_tree_domain
from program_management.ddd.validators import _attach_finality_end_date
from program_management.ddd.validators import _attach_option


class ValidateFinalitiesEndDateAndOptions(business_validator.BusinessValidator):
    def __init__(
            self,
            node_to_paste_to: 'Node',
            node_to_paste: 'Node',
            tree_repository: 'ProgramTreeRepository',
            tree_version_repository: 'ProgramTreeVersionRepository'
    ):
        super().__init__()
        self.node_to_paste = node_to_paste
        self.tree_repository = tree_repository
        self.tree_version_repository = tree_version_repository
        self.node_to_paste_to = node_to_paste_to

    def validate(self, *args, **kwargs):
        tree_identity = program_tree_domain.ProgramTreeIdentity(
            code=self.node_to_paste.code,
            year=self.node_to_paste.academic_year.year
        )
        tree_from_node_to_paste = self.tree_repository.get(tree_identity)
        tree_version_from_node_to_paste = self.tree_version_repository.search_versions_from_trees(
            [tree_from_node_to_paste]
        )[0]
        _attach_finality_end_date.AttachFinalityEndDateValidator(
            updated_tree_version=tree_version_from_node_to_paste,
        ).validate()
        _attach_option.AttachOptionsValidator(
            program_tree_repository=self.tree_repository,
            tree_from_node_to_paste=tree_from_node_to_paste,
        ).validate()
