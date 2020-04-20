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
from django.db.models import Prefetch

from base.business.education_groups import create
from base.models.education_group import EducationGroup
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories


class ProgramGenerators:
    def __init__(self):
        self.trainings = EducationGroup.objects.filter(
            educationgroupyear__education_group_type__category=education_group_categories.TRAINING
        ).prefetch_related(
            Prefetch(
                "educationgroupyear_set",
                EducationGroupYear.objects.order_by("academic_year__year"),
                to_attr="educationgroupyears"
            )
        )

        self._create_initial_structure()

    def _create_initial_structure(self):
        for training in self.trainings:
            create.create_initial_group_element_year_structure(list(training.educationgroupyears))

        EducationGroupYear.objects.exclude(education_group_type__category=education_group_categories.TRAINING)
