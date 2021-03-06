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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import random

import factory

from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.utils.fuzzy import FuzzyBoolean
from reference.tests.factories.country import CountryFactory


class EntityVersionAddressFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'base.EntityVersionAddress'
    
    city = factory.Faker('city')
    street = factory.Faker('street_name')
    street_number = random.randint(1, 1000)
    postal_code = factory.Faker('postcode')
    state = factory.Faker('text', max_nb_chars=255)
    country = factory.SubFactory(CountryFactory)
    entity_version = factory.SubFactory(EntityVersionFactory)
    location = None
    is_main = FuzzyBoolean()


class MainRootEntityVersionAddressFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'base.EntityVersionAddress'

    city = factory.Faker('city')
    street = factory.Faker('street_name')
    street_number = random.randint(1, 1000)
    postal_code = factory.Faker('postcode')
    state = factory.Faker('text', max_nb_chars=255)
    country = factory.SubFactory(CountryFactory)
    entity_version = factory.SubFactory(EntityVersionFactory, parent=None)
    location = None
    is_main = True
