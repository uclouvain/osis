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
from unittest import mock

from django.test import SimpleTestCase

from program_management.ddd import command
from program_management.ddd.service.read import node_identity_service


class TestNodeIdentityService(SimpleTestCase):
    @mock.patch('program_management.ddd.service.read.node_identity_service.NodeIdentitySearch')
    def test_assert_call_node_identity_business_service(self, mock_identity_search):
        cmd = command.GetNodeIdentityFromElementId(element_id=4454)
        node_identity_service.get_node_identity_from_element_id(cmd)

        self.assertTrue(mock_identity_search.get_from_element_id.called)
