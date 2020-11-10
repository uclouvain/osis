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
from education_group.ddd.domain.exception import TrainingHaveLinkWithEPC, MiniTrainingHaveLinkWithEPC
from education_group.ddd.domain.service.link_with_epc import LinkWithEPC


class TrainingLinkWithEPCValidator(business_validator.BusinessValidator):
    def __init__(self, training_id: 'TrainingIdentity'):
        super().__init__()
        self.training_id = training_id

    def validate(self, *args, **kwargs):
        if LinkWithEPC().is_training_have_link_with_epc(self.training_id):
            raise TrainingHaveLinkWithEPC(self.training_id.acronym, self.training_id.year)


class MiniTrainingLinkWithEPCValidator(business_validator.BusinessValidator):
    def __init__(self, mini_training_id: 'MiniTrainingIdentity'):
        super().__init__()
        self.mini_training_id = mini_training_id

    def validate(self, *args, **kwargs):
        if LinkWithEPC().is_mini_training_have_link_with_epc(self.mini_training_id):
            raise MiniTrainingHaveLinkWithEPC(self.mini_training_id.acronym, self.mini_training_id.year)
