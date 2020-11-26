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

from django.test import SimpleTestCase
from django.utils.translation import gettext as _

from base.ddd.utils import business_validator
from base.tests.factories.academic_year import AcademicYearFactory
from program_management.ddd.domain.exception import CannotPasteNodeToHimselfException, CannotAttachParentNodeException
from program_management.ddd.domain.program_tree import build_path
from program_management.ddd.validators._infinite_recursivity import InfiniteRecursivityTreeValidator, \
    InfiniteRecursivityLinkValidator
from program_management.tests.ddd.factories.node import NodeGroupYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.factories.repository.fake import get_fake_program_tree_repository
from program_management.tests.ddd.validators.mixins import TestValidatorValidateMixin


class TestInfiniteRecursivityTreeValidator(TestValidatorValidateMixin, SimpleTestCase):

    def setUp(self):
        """
        root
         |---- child_of_root
        """
        self.academic_year = AcademicYearFactory.build(current=True)

        self.root = NodeGroupYearFactory(year=self.academic_year.year)
        self.child_of_root = NodeGroupYearFactory(year=self.academic_year.year)
        self.root.add_child(self.child_of_root)

        self.tree = ProgramTreeFactory(root_node=self.root)
        self.path_to_child_of_root = build_path(self.root, self.child_of_root)
        self.path_to_root = build_path(self.root)

        self.fake_program_tree_repository = get_fake_program_tree_repository([self.tree])

    def test_should_not_raise_eception_when_no_recursivity_found(self):
        node_to_attach = NodeGroupYearFactory(year=self.academic_year.year)
        self.assertValidatorNotRaises(InfiniteRecursivityTreeValidator(
            self.tree,
            node_to_attach,
            self.path_to_root,
            self.fake_program_tree_repository
        ))

    def test_when_node_to_paste_is_parent_of_node_where_to_paste(self):
        node_to_paste = self.root
        path_where_to_paste = self.path_to_child_of_root

        self.fake_program_tree_repository.root_entities.append(ProgramTreeFactory(root_node=node_to_paste))

        with self.assertRaises(CannotAttachParentNodeException):
            InfiniteRecursivityTreeValidator(
                self.tree,
                node_to_paste,
                path_where_to_paste,
                self.fake_program_tree_repository
            ).validate()

    def test_when_node_to_paste_contains_child_that_is_parent_of_node_where_to_paste(self):
        node_to_paste = NodeGroupYearFactory(
            year=self.academic_year.year,
        )  # node not used in tree where to paste ...
        node_to_paste.add_child(self.child_of_root)  # ... but the child is one of the parent where to paste.

        self.fake_program_tree_repository.root_entities.append(ProgramTreeFactory(root_node=node_to_paste))
        where_to_paste = self.path_to_child_of_root

        with self.assertRaises(CannotAttachParentNodeException):
            InfiniteRecursivityTreeValidator(
                self.tree,
                node_to_paste,
                where_to_paste,
                self.fake_program_tree_repository
            ).validate()


class TestInfiniteRecursivityLinkValidator(TestValidatorValidateMixin, SimpleTestCase):
    def setUp(self):
        self.tree = ProgramTreeFactory()

    def test_should_not_raise_exception_when_no_recursivity_found(self):
        node_to_attach = NodeGroupYearFactory()

        self.assertValidatorNotRaises(InfiniteRecursivityLinkValidator(self.tree.root_node, node_to_attach))

    def test_should_raise_exception_when_adding_node_to_himself(self):
        with self.assertRaises(CannotPasteNodeToHimselfException):
            InfiniteRecursivityLinkValidator(self.tree.root_node, self.tree.root_node).validate()
