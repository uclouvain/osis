##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
import datetime

import factory.fuzzy

from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory


class EntityComponentYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.EntityComponentYear"

    external_id = factory.Sequence(lambda n: '10000000%02d' % n)
    changed = factory.fuzzy.FuzzyNaiveDateTime(
        datetime.datetime(2016, 1, 1),
        datetime.datetime(2017, 3, 1,)
    )

    entity_container_year = factory.SubFactory(EntityContainerYearFactory)
    learning_component_year = factory.SubFactory(LearningComponentYearFactory)
    repartition_volume = factory.fuzzy.FuzzyDecimal(9)
