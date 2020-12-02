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
import operator
from decimal import Decimal

import factory.fuzzy

from base.models.enums import learning_component_year_type


class LearningComponentYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.LearningComponentYear"

    learning_unit_year = factory.SubFactory("base.tests.factories.learning_unit_year.LearningUnitYearFactory")
    acronym = factory.Sequence(lambda n: '%d' % n)
    type = factory.Iterator(learning_component_year_type.LEARNING_COMPONENT_YEAR_TYPES, getter=operator.itemgetter(0))
    comment = factory.Sequence(lambda n: 'Comment-%d' % n)
    planned_classes = factory.fuzzy.FuzzyInteger(1, 10)
    hourly_volume_total_annual = factory.LazyAttribute(
        lambda obj: obj.hourly_volume_partial_q1 + obj.hourly_volume_partial_q2
    )
    hourly_volume_partial_q1 = factory.fuzzy.FuzzyDecimal(0, 30, precision=0)
    hourly_volume_partial_q2 = factory.fuzzy.FuzzyDecimal(0, 30, precision=0)
    repartition_volume_requirement_entity = factory.LazyAttribute(
        lambda obj: (obj.hourly_volume_partial_q1 + obj.hourly_volume_partial_q2) * obj.planned_classes
    )
    repartition_volume_additional_entity_1 = Decimal(0)
    repartition_volume_additional_entity_2 = Decimal(0)

    @factory.post_generation
    def consistency_of_planned_classes_and_volumes(self, create, extracted, ** kwargs):
        if self.hourly_volume_total_annual is None or self.hourly_volume_total_annual == 0:
            self.planned_classes = 0
            self.repartition_volume_requirement_entity = self.vol_global


class LecturingLearningComponentYearFactory(LearningComponentYearFactory):
    type = learning_component_year_type.LECTURING
    acronym = "PM"


class PracticalLearningComponentYearFactory(LearningComponentYearFactory):
    type = learning_component_year_type.PRACTICAL_EXERCISES
    acronym = "TP"
