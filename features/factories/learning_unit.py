############################################################################
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
############################################################################
import random

import factory

from base.models.academic_year import AcademicYear, compute_max_academic_year_adjournment
from base.models.campus import Campus
from base.models.entity_version import EntityVersion
from base.models.enums.entity_type import FACULTY
from base.models.enums.organization_type import MAIN
from base.tests.factories.learning_unit import LearningUnitFactoryWithAnnualizedData

LEARNING_UNIT_START_YEAR = 2015


class LearningUnitGenerator:
    def __init__(self):
        entities_version = list(EntityVersion.objects.filter(entity_type=FACULTY).select_related("entity"))
        campuses = list(Campus.objects.filter(organization__type=MAIN))
        academic_years_range = AcademicYear.objects.filter(
            year__gte=LEARNING_UNIT_START_YEAR,
            year__lte=compute_max_academic_year_adjournment()
        )
        self.learning_units = LearningUnitFactoryWithAnnualizedData.create_batch(
            40,
            start_year__year=LEARNING_UNIT_START_YEAR,
            learningunityears__academic_years=academic_years_range,
            learningunityears__learning_container_year__requirement_entity=factory.Iterator(
                entities_version, getter=lambda ev: ev.entity
            ),
            learningunityears__campus=factory.LazyFunction(lambda: random.choice(campuses))
        )
