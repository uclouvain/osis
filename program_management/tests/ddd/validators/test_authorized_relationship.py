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
import copy

from django.test import SimpleTestCase
from django.utils.translation import gettext as _

from base.tests.factories.academic_year import AcademicYearFactory
from program_management.ddd.domain.authorized_relationship import AuthorizedRelationshipList, AuthorizedRelationship
from program_management.ddd.validators._authorized_relationship import AttachAuthorizedRelationshipValidator, \
    DetachAuthorizedRelationshipValidator
from program_management.tests.ddd.factories.node import NodeEducationGroupYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory


class TestAttachAuthorizedRelationshipValidator(SimpleTestCase):

    def setUp(self):
        self.academic_year = AcademicYearFactory.build(current=True)

        self.root_node = NodeEducationGroupYearFactory(
            year=self.academic_year.year,
        )
        self.common_core_node = NodeEducationGroupYearFactory(
            year=self.academic_year.year,
        )
        self.authorized_relationships = AuthorizedRelationshipList([
            AuthorizedRelationship(
                parent_type=self.root_node.node_type,
                child_type=self.common_core_node.node_type,
                min_constraint=1,
                max_constraint=1,
            )
        ])

    def test_success(self):
        tree = ProgramTreeFactory(root_node=self.root_node, authorized_relationships=self.authorized_relationships)
        validator = AttachAuthorizedRelationshipValidator(tree, self.common_core_node, self.root_node)
        self.assertTrue(validator.is_valid())

    def test_when_maximum_children_reached(self):
        root_node = copy.deepcopy(self.root_node)
        root_node.add_child(self.common_core_node)
        tree = ProgramTreeFactory(root_node=root_node, authorized_relationships=self.authorized_relationships)
        validator = AttachAuthorizedRelationshipValidator(tree, self.common_core_node, root_node)

        self.assertFalse(validator.is_valid())

        max_error_msg = _("The parent must have at least one child of type(s) \"%(types)s\".") % {
            "types": str(tree.authorized_relationships.get_authorized_children_types(self.root_node))
        }
        self.assertIn(max_error_msg, validator.error_messages)
        self.assertEqual(len(validator.error_messages), 1)

    def test_when_unauthorized_relation(self):
        tree = ProgramTreeFactory(root_node=self.root_node, authorized_relationships=self.authorized_relationships)
        unauthorized_node_to_attach = NodeEducationGroupYearFactory(
            year=self.academic_year.year,
        )
        validator = AttachAuthorizedRelationshipValidator(tree, unauthorized_node_to_attach, self.root_node)
        self.assertFalse(validator.is_valid())
        error_msg = _("You cannot add \"%(child_types)s\" to \"%(parent)s\" (type \"%(parent_type)s\")") % {
            'child_types': unauthorized_node_to_attach.node_type.value,
            'parent': self.root_node,
            'parent_type': self.root_node.node_type.value,
        }

        self.assertIn(error_msg, validator.error_messages)


class TestDetachAuthorizedRelationshipValidator(SimpleTestCase):

    def setUp(self):
        self.academic_year = AcademicYearFactory.build(current=True)

        self.root_node = NodeEducationGroupYearFactory(
            year=self.academic_year.year,
        )
        self.common_core_node = NodeEducationGroupYearFactory(
            year=self.academic_year.year,
        )
        self.authorized_relationships = AuthorizedRelationshipList([
            AuthorizedRelationship(
                parent_type=self.root_node.node_type,
                child_type=self.common_core_node.node_type,
                min_constraint=1,
                max_constraint=1,
            )
        ])

    def test_success(self):
        tree = ProgramTreeFactory(root_node=self.root_node, authorized_relationships=self.authorized_relationships)
        validator = DetachAuthorizedRelationshipValidator(tree, self.common_core_node, self.root_node)
        self.assertTrue(validator.is_valid())

    def test_when_minimum_children_reached(self):
        root_node = copy.deepcopy(self.root_node)
        root_node.add_child(self.common_core_node)
        tree = ProgramTreeFactory(root_node=root_node, authorized_relationships=self.authorized_relationships)
        validator = DetachAuthorizedRelationshipValidator(tree, self.common_core_node, root_node)
        self.assertFalse(validator.is_valid())
        error_msg = _("The number of children of type(s) \"%(child_types)s\" for \"%(parent)s\" "
                      "has already reached the limit.") % {
            'child_types': self.common_core_node.node_type.value,
            'parent': root_node
        }
        self.assertIn(error_msg, validator.error_messages)

    # TODO duplicated test
    def test_when_unauthorized_relation(self):
        tree = ProgramTreeFactory(root_node=self.root_node, authorized_relationships=self.authorized_relationships)
        unauthorized_node_to_attach = NodeEducationGroupYearFactory(
            year=self.academic_year.year,
        )
        validator = AttachAuthorizedRelationshipValidator(tree, unauthorized_node_to_attach, self.root_node)
        self.assertFalse(validator.is_valid())
        error_msg = _("You cannot add \"%(child_types)s\" to \"%(parent)s\" (type \"%(parent_type)s\")") % {
            'child_types': unauthorized_node_to_attach.node_type.value,
            'parent': self.root_node,
            'parent_type': self.root_node.node_type.value,
        }

        self.assertIn(error_msg, validator.error_messages)
