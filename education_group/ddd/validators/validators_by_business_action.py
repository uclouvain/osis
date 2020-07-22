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
from base.ddd.utils import business_validator
from education_group.ddd.domain import mini_training
from education_group.ddd.domain.group import Group
from education_group.ddd.validators._content_constraint import ContentConstraintValidator
from education_group.ddd.validators._credits import CreditsValidator
from education_group.ddd.validators.start_and_end_year_validator import StartAndEndYearValidator


class CreateGroupValidatorList(business_validator.BusinessListValidator):

    def __init__(
            self,
            group: 'Group'
    ):
        self.validators = [
            ContentConstraintValidator(group.content_constraint),
            CreditsValidator(group.credits),
        ]
        super().__init__()


class UpdateGroupValidatorList(business_validator.BusinessListValidator):

    def __init__(
            self,
            group: 'Group'
    ):
        self.validators = [
            ContentConstraintValidator(group.content_constraint),
            CreditsValidator(group.credits),
        ]
        super().__init__()


class CreateMiniTrainingValidatorList(business_validator.BusinessListValidator):
    def __init__(self, mini_training_domain_obj: mini_training.MiniTraining):
        self.validators = [
            ContentConstraintValidator(mini_training_domain_obj.content_constraint),
            StartAndEndYearValidator(mini_training_domain_obj.start_year, mini_training_domain_obj.end_year)
        ]
        super().__init__()
