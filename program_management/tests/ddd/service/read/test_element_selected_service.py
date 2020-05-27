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

from base.tests.factories.user import UserFactory
from base.utils import cache
from program_management.ddd.service.read import element_selected_service
from program_management.models.enums import node_type


class TestRetrieveElementsSelected(SimpleTestCase):
    def setUp(self):
        self.user = UserFactory.build()
        self.addCleanup(cache.ElementCache(self.user).clear)

    def test_when_no_elements_selected_then_should_return_empty_list(self):
        result = element_selected_service.retrieve_element_selected(self.user, [], None)
        self.assertEqual(
            result,
            []
        )

    def test_when_one_element_selected_stored_in_cache_then_should_return_a_list_of_dict(self):
        cache.ElementCache(self.user).save_element_selected_bis(45, node_type.NodeType.LEARNING_UNIT.name)

        result = element_selected_service.retrieve_element_selected(self.user, [], None)
        self.assertEqual(
            result,
            [(45, node_type.NodeType.LEARNING_UNIT, None)]
        )

    def test_when_ids_and_content_type_set_then_should_return_those_but_zipped(self):
        result = element_selected_service.retrieve_element_selected(self.user, [45, 18], node_type.NodeType.EDUCATION_GROUP.name)
        self.assertEqual(
            result,
            [(45, node_type.NodeType.EDUCATION_GROUP, None), (18, node_type.NodeType.EDUCATION_GROUP, None)]
        )
