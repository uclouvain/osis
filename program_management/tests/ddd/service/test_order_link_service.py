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
from django.test import SimpleTestCase

from program_management.ddd.service import order_link_service
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeGroupYearFactory, NodeLearningUnitYearFactory


class TestUpDownChildren(SimpleTestCase):

    def setUp(self):
        self.parent = NodeGroupYearFactory()
        self.link0 = LinkFactory(parent=self.parent, child=NodeLearningUnitYearFactory(), order=0)
        self.link1 = LinkFactory(parent=self.parent, child=NodeGroupYearFactory(), order=1)
        self.link2 = LinkFactory(parent=self.parent, child=NodeLearningUnitYearFactory(), order=2)

    def test_do_not_modify_order_when_applying_up_on_first_element(self):
        order_link_service.up_link(self.parent, self.link0)
        self.assertListEqual(
            self.parent.children,
            [self.link0, self.link1, self.link2]
        )

    def test_up_action_on_link_should_increase_order_by_one(self):
        order_link_service.up_link(self.parent, self.link1)
        self.assertListEqual(
            [self.link1.order, self.link0.order, self.link2.order],
            [0, 1, 2]
        )

    def test_down_action_on_link_should_decrease_order_by_one(self):
        order_link_service.down_link(self.parent, self.link1)
        self.assertListEqual(
            [self.link0.order, self.link2.order, self.link1.order],
            [0, 1, 2]
        )

    def test_do_not_modify_order_when_applying_down_on_last_element(self):
        order_link_service.down_link(self.parent, self.link2)
        self.assertListEqual(
            self.parent.children,
            [self.link0, self.link1, self.link2]
        )
