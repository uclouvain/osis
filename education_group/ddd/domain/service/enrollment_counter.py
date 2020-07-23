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
from osis_common.ddd import interface

from education_group.ddd.business_types import *
from base.models.offer_enrollment import OfferEnrollment


class EnrollmentCounter(interface.DomainService):
    def get_training_enrollments_count(self, training_id: 'TrainingIdentity') -> int:
        return self._get_count_queryset(training_id.acronym, training_id.year)

    def get_mini_training_enrollments_count(self, mini_training_id: 'MiniTrainingIdentity') -> int:
        return self._get_count_queryset(mini_training_id.acronym, mini_training_id.year)

    def _get_count_queryset(self, acronym: str, year: int):
        return OfferEnrollment.objects.filter(
            education_group_year__acronym=acronym,
            education_group_year__academic_year__year=year
        ).count()
