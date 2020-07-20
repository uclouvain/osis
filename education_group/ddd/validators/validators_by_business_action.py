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
from education_group.ddd.validators._credits import CreditsValidator

from base.ddd.utils import business_validator
from education_group.ddd.business_types import *
from education_group.ddd.validators._content_constraint import ContentConstraintValidator
from education_group.ddd.validators._enrollments import TrainingEnrollmentsValidator, MiniTrainingEnrollmentsValidator
from education_group.ddd.validators._link_with_epc import TrainingLinkWithEPCValidator, MiniTrainingLinkWithEPCValidator


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


class DeleteOrphanGroupValidatorList(business_validator.BusinessListValidator):

    def __init__(
            self,
            group: 'Group',
    ):
        self.validators = []
        super().__init__()


class DeleteOrphanTrainingValidatorList(business_validator.BusinessListValidator):

    def __init__(
            self,
            training: 'Training',
    ):
        self.validators = [
            TrainingEnrollmentsValidator(training.entity_id),
            TrainingLinkWithEPCValidator(training.entity_id)
        ]
        super().__init__()


class DeleteOrphanMiniTrainingValidatorList(business_validator.BusinessListValidator):

    def __init__(
            self,
            mini_training: 'MiniTraining',
    ):
        self.validators = [
            MiniTrainingEnrollmentsValidator(mini_training.entity_id),
            MiniTrainingLinkWithEPCValidator(mini_training.entity_id)
        ]
        super().__init__()
