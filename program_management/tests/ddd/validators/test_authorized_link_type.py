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

from base.models.enums.link_type import LinkTypes
from program_management.ddd.validators._authorized_link_type import AuthorizedLinkTypeValidator
from program_management.tests.ddd.factories.node import NodeLearningUnitYearFactory, NodeEducationGroupYearFactory


class TestAuthorizedLinkTypeValidator(SimpleTestCase):
    def test_a_reference_link_with_a_learning_unit_as_child_should_not_be_valid(self):
        learning_unit_node_to_add = NodeLearningUnitYearFactory()
        link_type = LinkTypes.REFERENCE
        validator = AuthorizedLinkTypeValidator(learning_unit_node_to_add, link_type)
        self.assertFalse(validator.is_valid())

    def test_a_none_reference_link_with_a_learning_unit_as_child_should_be_valid(self):
        learning_unit_node_to_add = NodeLearningUnitYearFactory()
        link_type = None
        validator = AuthorizedLinkTypeValidator(learning_unit_node_to_add, link_type)
        self.assertTrue(validator.is_valid())

    def test_a_link_with_an_education_group_as_child_should_be_valid_whatever_the_link_type(self):
        education_group_node_to_add = NodeEducationGroupYearFactory()

        link_types = (None, LinkTypes.REFERENCE)
        for link_type in link_types:
            with self.subTest(link_type=link_type):
                validator = AuthorizedLinkTypeValidator(education_group_node_to_add, link_type)
                self.assertTrue(validator.is_valid())
