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
from education_group.ddd.business_types import *
from education_group.ddd.domain.exception import CannotCopyMiniTrainingDueToEndDate


class CheckMiniTrainingEndDateValidator(business_validator.BusinessValidator):
    def __init__(self, mini_training: 'MiniTraining'):
        super().__init__()
        self.mini_training = mini_training

    def validate(self, *args, **kwargs):
        if self.mini_training.end_year and self.mini_training.year >= self.mini_training.end_year:
            raise CannotCopyMiniTrainingDueToEndDate(mini_training=self.mini_training)
