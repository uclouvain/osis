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

from base.models.enums.education_group_types import TrainingType, GroupType
from program_management.ddd.domain.exception import CannotDetachLearningUnitsWhoArePrerequisiteException, \
    CannotDetachLearningUnitsWhoHavePrerequisiteException
from program_management.ddd.validators._has_or_is_prerequisite import _IsPrerequisiteValidator, \
    _HasPrerequisiteValidator
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeLearningUnitYearFactory, NodeGroupYearFactory
from program_management.tests.ddd.factories.prerequisite import cast_to_prerequisite
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.validators.mixins import TestValidatorValidateMixin


class TestIsPrerequisiteValidator(TestValidatorValidateMixin, SimpleTestCase):

    def setUp(self):
        link = LinkFactory(parent__node_type=TrainingType.BACHELOR, child__node_type=GroupType.COMMON_CORE)
        self.tree = ProgramTreeFactory(root_node=link.parent)
        self.common_core = link.child
        link_with_learn_unit = LinkFactory(
            parent=self.common_core,
            child=NodeLearningUnitYearFactory(is_prerequisite_of=[])
        )
        self.node_learning_unit = link_with_learn_unit.child

    def test_should_not_raise_exception_when_children_of_node_to_detach_are_not_prerequisites(self):
        node_to_detach = self.common_core
        LinkFactory(parent=self.common_core, child=NodeLearningUnitYearFactory(is_prerequisite_of=[]))
        LinkFactory(parent=self.common_core, child=NodeLearningUnitYearFactory(is_prerequisite_of=[]))

        validator = _IsPrerequisiteValidator(self.tree, node_to_detach)
        self.assertValidatorNotRaises(validator)

    def test_should_raise_exception_when_children_of_node_to_detach_are_prerequisites(self):
        node_to_detach = self.common_core
        link = LinkFactory(parent=self.tree.root_node, child=NodeLearningUnitYearFactory(is_prerequisite_of=[]))
        link_with_child_that_is_prerequisite = LinkFactory(
            parent=self.common_core,
            child=NodeLearningUnitYearFactory(is_prerequisite_of=[link.child])
        )

        with self.assertRaises(CannotDetachLearningUnitsWhoArePrerequisiteException):
            _IsPrerequisiteValidator(self.tree, node_to_detach).validate()

    def test_should_raise_exception_when_node_to_detach_is_prerequisite(self):
        link_with_child_is_prerequisite = LinkFactory(
            parent=self.common_core,
            child=NodeLearningUnitYearFactory(is_prerequisite_of=[self.node_learning_unit])
        )
        node_to_detach = link_with_child_is_prerequisite.child

        with self.assertRaises(CannotDetachLearningUnitsWhoArePrerequisiteException):
            _IsPrerequisiteValidator(self.tree, node_to_detach).validate()

    def test_should_not_raise_exception_when_node_to_detach_is_prerequisite_twice(self):
        learning_unit_that_is_prerequisite = NodeLearningUnitYearFactory(is_prerequisite_of=[self.node_learning_unit])
        link_with_child_is_prerequisite = LinkFactory(
            parent=self.common_core,
            child=learning_unit_that_is_prerequisite  # learning unit used once
        )
        link_with_child_is_prerequisite_2 = LinkFactory(
            parent=self.tree.root_node,
            child=learning_unit_that_is_prerequisite  # learning unit used twice
        )
        node_to_detach = link_with_child_is_prerequisite.child

        assertion = "While the prerequisite is used more than once in the same tree, we can detach it"
        self.assertValidatorNotRaises(_IsPrerequisiteValidator(self.tree, node_to_detach))


class TestHasPrerequisiteValidator(TestValidatorValidateMixin, SimpleTestCase):

    def setUp(self):
        self.node_is_prerequisite = NodeLearningUnitYearFactory()

        node_has_prerequisite = NodeLearningUnitYearFactory()
        node_has_prerequisite.set_prerequisite(cast_to_prerequisite(self.node_is_prerequisite))
        self.node_has_prerequisite = node_has_prerequisite

    def test_should_not_raise_exception_when_children_of_node_to_detach_do_not_have_prerequisites(self):
        node_to_detach = NodeGroupYearFactory()
        link = LinkFactory(child=node_to_detach)
        tree = ProgramTreeFactory(root_node=link.parent)

        validator = _HasPrerequisiteValidator(tree, node_to_detach)
        self.assertValidatorNotRaises(validator)

    def test_should_raise_exception_when_children_of_node_to_detach_have_prerequisites(self):
        node_to_detach = NodeGroupYearFactory()

        link = LinkFactory(child=node_to_detach)
        LinkFactory(parent=node_to_detach, child=self.node_has_prerequisite)
        LinkFactory(parent=self.node_has_prerequisite, child=self.node_is_prerequisite)

        tree = ProgramTreeFactory(root_node=link.parent)

        with self.assertRaises(CannotDetachLearningUnitsWhoHavePrerequisiteException):
            _HasPrerequisiteValidator(tree, node_to_detach).validate()

    def test_should_raise_exception_when_node_to_detach_is_learning_unit_that_has_prerequisite(self):
        node_to_detach_has_prerequisite = self.node_has_prerequisite

        link = LinkFactory(child=node_to_detach_has_prerequisite)

        tree = ProgramTreeFactory(root_node=link.parent)

        with self.assertRaises(CannotDetachLearningUnitsWhoHavePrerequisiteException):
            _HasPrerequisiteValidator(tree, node_to_detach_has_prerequisite).validate()

    def test_should_not_raise_exception_when_node_to_detach_has_prerequisite_twice(self):
        tree = ProgramTreeFactory()
        LinkFactory(
            parent=tree.root_node,
            child=self.node_is_prerequisite,
        )
        LinkFactory(
            parent=tree.root_node,
            child=LinkFactory(
                child=self.node_has_prerequisite
            ).parent
        )  # node_has_prerequisite used once
        LinkFactory(
            parent=tree.root_node,
            child=LinkFactory(
                child=self.node_has_prerequisite
            ).parent
        )  # node_has_prerequisite used twice

        assertion = "While the prerequisite is used more than once in the same tree, we can detach it"
        self.assertValidatorNotRaises(_HasPrerequisiteValidator(tree, self.node_has_prerequisite))
