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
from django.db.models import Q

from osis_common.ddd import interface
from program_management.ddd.business_types import *
from program_management.models.education_group_version import EducationGroupVersion


class HasVersionWithGreaterEndYear(interface.DomainService):

    @classmethod
    def greater_than_standard_year(cls, standard_version: 'ProgramTreeVersion') -> bool:
        return EducationGroupVersion.objects.filter(
            Q(root_group__group__end_year__isnull=True) |
            Q(root_group__group__end_year__year__gte=standard_version.entity_id.year),
            offer__acronym=standard_version.entity_id.offer_acronym,
        ).exclude(
            version_name=standard_version.version_name
        ).exists()

    @classmethod
    def inferior_than_version(cls, specific_version: 'ProgramTreeVersion') -> bool:
        return EducationGroupVersion.standard.filter(
            offer__education_group__end_year__year__lte=specific_version.entity_id.year,
            offer__acronym=specific_version.entity_id.offer_acronym,
        ).exists()
