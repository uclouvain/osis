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
from typing import Callable

from base.ddd.utils import business_validator
from program_management.ddd.domain.exception import ProgramTreeNonEmpty
from education_group.ddd.domain.group import GroupIdentity


class EmptyValidator(business_validator.BusinessValidator):
    def __init__(self, group_id: GroupIdentity, is_empty_content_service: Callable):
        super().__init__()
        self.group_id = group_id
        self.is_empty_content_service = is_empty_content_service

    def validate(self, *args, **kwargs):
        if not self.is_empty_content_service(code=self.group_id.code, year=self.group_id.year):
            raise ProgramTreeNonEmpty
