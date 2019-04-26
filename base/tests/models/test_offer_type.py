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
from base.models import offer_type

from base.tests.factories.offer_type import OfferTypeFactory
from django.test import TestCase
from django.utils import timezone


class OfferTypeTest(TestCase):

    def test_find_all_result_none(self):
        self.assertEqual(len(offer_type.find_all()), 0)

    def test_find_all_existing_results(self):
        an_offer_type_1 = offer_type.OfferType(name="Bachelier")
        an_offer_type_1.save()
        an_offer_type_2 = offer_type.OfferType(name="Doctorat")
        an_offer_type_2.save()

        self.assertEqual(len(offer_type.find_all()), 2)


    def test_find_all_distinct_existing_results(self):
        an_offer_type_1 = offer_type.OfferType(name="Bachelier")
        an_offer_type_1.save()
        an_offer_type_2 = offer_type.OfferType(name="Bachelier")
        an_offer_type_2.save()

        self.assertEqual(len(offer_type.find_all()), 1)