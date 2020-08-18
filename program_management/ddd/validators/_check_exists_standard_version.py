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
import attr

from base.ddd.utils import business_validator
from program_management.ddd.business_types import *
from program_management.ddd.domain import exception


class CheckExistsStandardVersionValidator(business_validator.BusinessValidator):
    def __init__(self, tree_version: 'ProgramTreeVersion', version_repository: 'ProgramTreeVersionRepository'):
        self.tree_version = tree_version
        self.version_repository = version_repository
        super().__init__()

    def validate(self, *args, **kwargs):
        if self.tree_version.is_standard:
            return

        standard_identity_next_year = attr.evolve(
            self.tree_version.entity_id,
            year=self.tree_version.entity_id.year+1,
            version_name=""
        )
        try:
            self.version_repository.get(standard_identity_next_year)
        except exception.ProgramTreeVersionNotFoundException:
            raise exception.CannotCopyTreeVersionDueToStandardNotExisting(self.tree_version)
