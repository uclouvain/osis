##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase

from reference.models.domain import Domain
from reference.tests.factories.decree import DecreeFactory
from reference.tests.factories.domain import DomainFactory


class TestDomain(TestCase):

    def setUp(self):
        self.decree = DecreeFactory(name='Paysage')
        self.decree2 = DecreeFactory(name='Bologne')

        DomainFactory(
            decree=self.decree,
            code='11',
            name='Test1'
        )
        DomainFactory(
            decree=self.decree,
            code='1',
            name='Test2'
        )
        DomainFactory(
            decree=self.decree,
            code='5',
            name='Test3'
        )
        DomainFactory(
            decree=self.decree,
            code='33',
            name='Test4'
        )
        DomainFactory(
            decree=self.decree2,
            code='11a',
            name='Test1b'
        )
        DomainFactory(
            decree=self.decree2,
            code='1b',
            name='Test2b'
        )
        DomainFactory(
            decree=self.decree2,
            code='5d',
            name='Test3b'
        )
        DomainFactory(
            decree=self.decree2,
            code='33t',
            name='Test4b'
        )

    def test_str(self):
        dom = DomainFactory(decree=self.decree, code='10H', name='Test Domain')
        expected_value = "{decree}: {code} {name}".format(decree=dom.decree.name,
                                                          code=dom.code,
                                                          name=dom.name)
        self.assertEqual(str(dom), expected_value)

    def test_str_without_decree_and_code(self):
        dom = DomainFactory(decree=None, code='', name='Test Domain')
        expected_value = "{name}".format(name=dom.name)
        self.assertEqual(str(dom), expected_value)

    def test_str_without_decree(self):
        dom = DomainFactory(decree=None, code='10H', name='Test Domain')
        expected_value = "{code} {name}".format(code=dom.code,
                                                name=dom.name)
        self.assertEqual(str(dom), expected_value)

    def test_str_without_code(self):
        dom = DomainFactory(decree=self.decree, code='', name='Test Domain')
        expected_value = "{decree}: {name}".format(decree=dom.decree.name,
                                                   name=dom.name)
        self.assertEqual(str(dom), expected_value)

    def test_sorting_domain(self):
        """ This test ensure that default order is state [DSC decree__name] + formation [ASC code]
        There is no need to test if the last code of a decree is higher than the first of the next decree.
        """
        domains = Domain.objects.all()
        previous_domain = domains.first().decree.name

        for d in domains:
            self.assertLessEqual(d.decree.name, previous_domain)
            previous_domain = d.decree.name

        previous_domain_id = domains.first().decree
        previous_code = '0'
        for d in domains:
            if d.decree == previous_domain_id:
                self.assertGreater(d.code, previous_code)
            previous_domain_id = d.decree
            previous_code = d.code
