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
from education_group.ddd.validators._abbreviated_title_already_exist import AcronymAlreadyExistValidator
from education_group.ddd.validators._acronym_required import AcronymRequiredValidator
from education_group.ddd.validators._certificate_aim_type_2 import CertificateAimType2Validator
from education_group.ddd.validators._copy_check_end_date import CheckEndDateValidator
from education_group.ddd.validators._credits import CreditsValidator
from education_group.ddd.business_types import *

from base.ddd.utils import business_validator
from education_group.ddd.validators._content_constraint import ContentConstraintValidator
from education_group.ddd.validators._start_year_end_year import StartYearEndYearValidator


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


class CreateTrainingValidatorList(business_validator.BusinessListValidator):

    def __init__(
            self,
            training: 'Training'
    ):
        self.validators = [
            AcronymRequiredValidator(training),
            AcronymAlreadyExistValidator(training),
            StartYearEndYearValidator(training),
            CertificateAimType2Validator(training),
        ]
        super().__init__()


class CopyTrainingValidatorList(business_validator.BusinessListValidator):

    def __init__(
            self,
            training_from: 'Training'
    ):
        self.validators = [
            CheckEndDateValidator(training_from),
        ]
        super().__init__()
