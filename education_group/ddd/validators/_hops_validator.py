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
from education_group.ddd.domain._hops import HOPS
from education_group.ddd.domain.exception import HopsDataShouldBeGreaterOrEqualsThanZeroAndLessThan9999


class HopsValuesValidator(business_validator.BusinessValidator):

    def __init__(self, hops: HOPS):
        super().__init__()
        self.ares_code = hops.ares_code
        self.ares_graca = hops.ares_graca
        self.ares_authorization = hops.ares_authorization

    def validate(self, *args, **kwargs):
        if not (0 < self.ares_code <= 9999) or \
                not (0 < self.ares_graca <= 9999) or \
                not (0 < self.ares_authorization <= 9999):
            raise HopsDataShouldBeGreaterOrEqualsThanZeroAndLessThan9999()
