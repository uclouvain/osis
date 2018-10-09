##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
import datetime

import factory
from factory.fuzzy import FuzzyDate

from base.tests.factories.organization import OrganizationFactory
from osis_common.utils.datetime import get_tzinfo


class OrganizationVersionFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'base.OrganizationVersion'

    external_id = factory.Faker('text', max_nb_chars=100)
    changed = factory.Faker('date_time_this_month', tzinfo=get_tzinfo())

    name = factory.Faker('text', max_nb_chars=255)
    acronym = factory.Faker('text', max_nb_chars=15)
    website = factory.Faker('url')
    prefix = factory.Faker('text', max_nb_chars=30)

    start_date = FuzzyDate(datetime.date(2015, 1, 1),
                           datetime.date(2015, 6, 30)).fuzz()

    organization = factory.SubFactory(OrganizationFactory)
