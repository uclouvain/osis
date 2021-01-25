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
import inspect
from unittest import mock
from unittest.mock import patch

from django.test import SimpleTestCase

import osis_common.ddd.interface
from base.ddd.utils.validation_message import MessageLevel, BusinessValidationMessage
from base.models.authorized_relationship import AuthorizedRelationshipList
from base.models.enums import prerequisite_operator
from base.models.enums.education_group_types import TrainingType, GroupType, MiniTrainingType
from base.models.enums.link_type import LinkTypes
from program_management.ddd.domain import node, exception
from program_management.ddd.domain import prerequisite
from program_management.ddd.domain import program_tree
from program_management.ddd.domain.link import Link
from program_management.ddd.domain.prerequisite import PrerequisiteItem
from program_management.ddd.domain.program_tree import ProgramTree
from program_management.ddd.domain.program_tree import build_path
from program_management.ddd.domain.service.generate_node_abbreviated_title import GenerateNodeAbbreviatedTitle
from program_management.ddd.domain.service.generate_node_code import GenerateNodeCode
from program_management.ddd.domain.service.validation_rule import FieldValidationRule
from program_management.ddd.repositories.program_tree import ProgramTreeRepository
from program_management.ddd.validators import validators_by_business_action
from program_management.ddd.validators.validators_by_business_action import DetachNodeValidatorList
from program_management.ddd.validators.validators_by_business_action import PasteNodeValidatorList
from program_management.models.enums import node_type
from program_management.tests.ddd.factories.authorized_relationship import AuthorizedRelationshipObjectFactory, \
    AuthorizedRelationshipListFactory, MandatoryRelationshipObjectFactory
from program_management.tests.ddd.factories.commands.paste_element_command import PasteElementCommandFactory
from program_management.tests.ddd.factories.domain.prerequisite.prerequisite import PrerequisitesFactory
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeGroupYearFactory, NodeLearningUnitYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.service.mixins import ValidatorPatcherMixin


class TestProgramTreeBuilderCopyToNextYear(SimpleTestCase):
    def setUp(self) -> None:
        self.authorized_relation = MandatoryRelationshipObjectFactory()
        self.authorized_relations_list = AuthorizedRelationshipListFactory(
            authorized_relationships=[self.authorized_relation]
        )
        self.copy_from_program_tree = ProgramTreeFactory(
            authorized_relationships=self.authorized_relations_list,
            root_node__node_type=self.authorized_relation.parent_type,
        )
        self.copy_from_program_tree.root_node.add_child(
            NodeGroupYearFactory(node_type=self.authorized_relation.child_type)
        )
        self.mock_repository = mock.create_autospec(ProgramTreeRepository)

    @mock.patch.object(GenerateNodeCode, 'generate_from_parent_node')
    @mock.patch.object(GenerateNodeAbbreviatedTitle, 'generate')
    @mock.patch.object(FieldValidationRule, 'get')
    @mock.patch('program_management.ddd.repositories.load_authorized_relationship.load')
    def test_should_create_new_program_tree_when_does_not_exist_for_next_year(self, mock_relationships, *mocks):
        mock_relationships.return_value = self.authorized_relations_list
        self.mock_repository.get.side_effect = exception.ProgramTreeNotFoundException

        resulted_tree = program_tree.ProgramTreeBuilder().copy_to_next_year(
            self.copy_from_program_tree,
            self.mock_repository
        )

        expected_identity = program_tree.ProgramTreeIdentity(
            code=self.copy_from_program_tree.entity_id.code,
            year=self.copy_from_program_tree.entity_id.year+1
        )
        self.assertEqual(expected_identity, resulted_tree.entity_id)
        self._assert_mandatory_children_are_created(resulted_tree)

    @mock.patch.object(GenerateNodeCode, 'generate_from_parent_node')
    @mock.patch.object(GenerateNodeAbbreviatedTitle, 'generate')
    @mock.patch.object(FieldValidationRule, 'get')
    @mock.patch('program_management.ddd.repositories.load_authorized_relationship.load')
    def test_should_not_create_mandatory_children_if_previous_year_does_not(self, mock_relationships, *mocks):
        """If the program tree from previous year is inconsistent, it's not the responsibility of the application code
        to fix these dirty data. To fix this, we need to create script to fix the dirty data and fix the business code
        in charge of creating program trees."""
        mock_relationships.return_value = self.authorized_relations_list
        self.mock_repository.get.side_effect = exception.ProgramTreeNotFoundException
        inconsistent_program_tree = ProgramTreeFactory(
            root_node__children=[],
            authorized_relationships=self.authorized_relations_list
        )
        self.mock_repository.update(inconsistent_program_tree)
        resulted_tree = program_tree.ProgramTreeBuilder().copy_to_next_year(
            inconsistent_program_tree,
            self.mock_repository
        )

        expected_identity = program_tree.ProgramTreeIdentity(
            code=inconsistent_program_tree.entity_id.code,
            year=inconsistent_program_tree.entity_id.year+1
        )
        self.assertEqual(expected_identity, resulted_tree.entity_id)
        self._assert_mandatory_children_are_not_created(resulted_tree)

    def _assert_mandatory_children_are_created(self, resulted_tree):
        children = resulted_tree.root_node.children_as_nodes
        self.assertEqual(len(children), 1)
        self.assertEqual(self.authorized_relation.child_type, children[0].node_type)

    def _assert_mandatory_children_are_not_created(self, resulted_tree):
        children = resulted_tree.root_node.children_as_nodes
        self.assertTrue(len(children) == 0)

    @mock.patch.object(GenerateNodeCode, 'generate_from_parent_node')
    @mock.patch.object(GenerateNodeAbbreviatedTitle, 'generate')
    @mock.patch.object(FieldValidationRule, 'get')
    @mock.patch('program_management.ddd.repositories.load_authorized_relationship.load')
    def test_should_return_existing_tree_when_exists_for_next_year(self, mock_relationships, *mocks):
        mock_relationships.return_value = self.authorized_relations_list
        program_tree_next_year = ProgramTreeFactory(
            authorized_relationships=self.authorized_relations_list,
            root_node__node_type=self.authorized_relation.parent_type,
        )
        self.mock_repository.get.return_value = program_tree_next_year

        resulted_tree = program_tree.ProgramTreeBuilder().copy_to_next_year(
            self.copy_from_program_tree,
            self.mock_repository
        )

        self.assertEqual(program_tree_next_year, resulted_tree)
        self._assert_mandatory_children_are_created(resulted_tree)


class TestGetNodeProgramTree(SimpleTestCase):
    def setUp(self):
        link = LinkFactory()
        self.root_node = link.parent
        self.subgroup_node = link.child
        self.tree = ProgramTreeFactory(root_node=self.root_node)

    def test_get_node_case_invalid_path(self):
        with self.assertRaises(node.NodeNotFoundException):
            self.tree.get_node(path='dummy_path')

    def test_get_node_case_children_path(self):
        valid_path = "|".join([str(self.root_node.pk), str(self.subgroup_node.pk)])
        result_node = self.tree.get_node(path=valid_path)

        self.assertEqual(result_node.pk, self.subgroup_node.pk)

    def test_get_node_case_root_node_path(self):
        result_node = self.tree.get_node(path=str(self.root_node.pk))
        self.assertEqual(
            result_node.pk,
            self.root_node.pk
        )


class TestGetNodeByIdAndTypeProgramTree(SimpleTestCase):
    def setUp(self):
        link = LinkFactory(child=NodeGroupYearFactory(node_id=1))
        self.root_node = link.parent
        self.subgroup_node = link.child

        link_with_learning_unit = LinkFactory(parent=self.root_node, child=NodeLearningUnitYearFactory(node_id=1))
        self.learning_unit_node = link_with_learning_unit.child

        self.tree = ProgramTreeFactory(root_node=self.root_node)

    def test_should_return_None_when_no_node_present_with_corresponding_node_id(self):
        result = self.tree.get_node_by_id_and_type(2, node_type.NodeType.LEARNING_UNIT)
        self.assertIsNone(result)

    def test_should_return_node_matching_specific_node_id_with_respect_to_class(self):
        result = self.tree.get_node_by_id_and_type(1, node_type.NodeType.LEARNING_UNIT)
        self.assertEqual(
            result,
            self.learning_unit_node
        )

        result = self.tree.get_node_by_id_and_type(1, node_type.NodeType.GROUP)
        self.assertEqual(
            result,
            self.subgroup_node
        )


class TestGetNodePath(SimpleTestCase):
    def setUp(self) -> None:
        self.tree = ProgramTreeFactory()
        self.link_1 = LinkFactory(parent=self.tree.root_node)
        self.link_1_1 = LinkFactory(parent=self.link_1.child)
        self.link_1_1_1 = LinkFactory(parent=self.link_1_1.child)
        self.link_2 = LinkFactory(parent=self.tree.root_node)
        self.link_2_1 = LinkFactory(parent=self.link_2.child, child=self.link_1_1_1.child)

    def test_when_node_not_present_in_tree_should_return_none(self):
        path = self.tree.get_node_smallest_ordered_path(NodeLearningUnitYearFactory())
        self.assertIsNone(path)

    def test_when_node_is_root_then_should_return_path_of_root(self):
        path = self.tree.get_node_smallest_ordered_path(self.tree.root_node)
        self.assertEqual(
            path,
            program_tree.build_path(self.tree.root_node)
        )

    def test_when_node_is_uniquely_present_in_tree_should_return_path(self):
        path = self.tree.get_node_smallest_ordered_path(self.link_1_1.child)
        self.assertEqual(
            path,
            program_tree.build_path(self.tree.root_node, self.link_1.child, self.link_1_1.child)
        )

    def test_when_node_is_present_multiple_times_in_tree_should_return_smallest_ordered_path(self):
        path = self.tree.get_node_smallest_ordered_path(self.link_1_1_1.child)

        path_expected = program_tree.build_path(
            self.tree.root_node,
            self.link_1.child,
            self.link_1_1.child,
            self.link_1_1_1.child
        )

        self.assertEqual(
            path,
            path_expected
        )


class TestGetAllLearningUnitNodes(SimpleTestCase):
    def setUp(self):
        link = LinkFactory(child=NodeGroupYearFactory())
        self.root_node = link.parent
        self.tree = ProgramTreeFactory(root_node=self.root_node)

    def test_should_return_empty_list_if_no_matching_type(self):
        result = self.tree.get_all_learning_unit_nodes()
        self.assertCountEqual(
            result,
            []
        )


class TestPasteNodeProgramTree(ValidatorPatcherMixin, SimpleTestCase):
    def setUp(self):
        root_node = NodeGroupYearFactory(node_id=0)
        self.tree = ProgramTreeFactory(root_node=root_node)
        self.child_to_paste = NodeGroupYearFactory()
        self.request = PasteElementCommandFactory(
            node_to_paste_code=self.child_to_paste.code,
            node_to_paste_year=self.child_to_paste.year,
            path_where_to_paste=str(self.tree.root_node.node_id)
        )

    def test_should_paste_node_to_position_indicated_by_path_when_validator_do_not_raise_exception(self):
        self.mock_validator_validate_to_not_raise_exception(PasteNodeValidatorList)

        link_created = self.tree.paste_node(self.child_to_paste, self.request, mock.Mock(), mock.Mock())
        self.assertIn(link_created, self.tree.root_node.children)

    def test_should_propagate_exception_and_not_paste_node_when_validator_raises_exception(self):
        self.mock_validator_validate_to_raise_exception(PasteNodeValidatorList, ["error message text"])

        with self.assertRaises(osis_common.ddd.interface.BusinessExceptions):
            self.tree.paste_node(self.child_to_paste, self.request, mock.Mock(), mock.Mock())

        self.assertNotIn(self.child_to_paste, self.tree.root_node.children_as_nodes)


class TestGetParentsUsingNodeAsReference(SimpleTestCase):
    def setUp(self):
        self.link_with_root = LinkFactory(parent__title='ROOT', child__title='child_ROOT')
        self.tree = ProgramTreeFactory(root_node=self.link_with_root.parent)

        self.link_with_ref = LinkFactory(
            parent=self.link_with_root.child,
            child__title='child__child__ROOT',
            link_type=LinkTypes.REFERENCE,
        )

    def test_when_node_is_not_used_as_reference(self):
        link_without_ref = LinkFactory(parent=self.link_with_root.child, link_type=None)
        result = self.tree.get_parents_using_node_with_respect_to_reference(link_without_ref.child)
        self.assertListEqual(result, [])

    def test_when_node_is_used_as_reference(self):
        result = self.tree.get_parents_using_node_with_respect_to_reference(self.link_with_ref.child)
        self.assertListEqual(
            result,
            [self.link_with_ref.parent]
        )

    def test_when_node_is_used_as_reference_twice(self):
        child_used_twice = self.link_with_ref.child

        another_link = LinkFactory(parent=self.link_with_root.parent)
        another_link_with_ref = LinkFactory(
            parent=another_link.child,
            child=child_used_twice,
            link_type=LinkTypes.REFERENCE
        )

        result = self.tree.get_parents_using_node_with_respect_to_reference(child_used_twice)

        self.assertCountEqual(result, [self.link_with_ref.parent, another_link_with_ref.parent])


class TestGetParents(SimpleTestCase):
    def setUp(self):
        self.link_with_root = LinkFactory(parent__title='ROOT', child__title='child_ROOT')
        self.tree = ProgramTreeFactory(root_node=self.link_with_root.parent)

        self.link_with_child = LinkFactory(
            parent=self.link_with_root.child,
            child__title='child__child__ROOT',
        )

        self.path = '{level1}|{level2}|{level3}'.format(
            level1=self.link_with_root.parent.node_id,
            level2=self.link_with_root.child.node_id,
            level3=self.link_with_child.child.node_id
        )

    def test_when_child_has_parents_on_2_levels(self):
        result = self.tree.get_parents(self.path)
        self.assertListEqual(
            result,
            [self.link_with_root.child, self.link_with_root.parent]
        )

    def test_when_child_has_multiple_parents(self):
        another_link_with_root = LinkFactory(parent=self.link_with_root.parent)
        another_link_with_child = LinkFactory(parent=another_link_with_root.child, child=self.link_with_child.child)
        result = self.tree.get_parents(self.path)

        self.assertNotIn(another_link_with_root.child, result)

        self.assertListEqual(
            result,
            [self.link_with_root.child, self.link_with_root.parent]
        )


class TestGetAllNodes(SimpleTestCase):

    def test_when_tree_has_not_children(self):
        tree = ProgramTreeFactory()
        self.assertSetEqual(tree.get_all_nodes(), {tree.root_node}, 'All nodes must include the root node')

    def test_when_tree_has_nodes_in_multiple_levels(self):
        link_with_root = LinkFactory(parent__title='ROOT', child__title='child_ROOT')
        link_with_child = LinkFactory(
            parent=link_with_root.child,
            child__title='child__child__ROOT',
        )
        tree = ProgramTreeFactory(root_node=link_with_root.parent)
        result = tree.get_all_nodes()
        self.assertSetEqual(
            result,
            {link_with_root.parent, link_with_root.child, link_with_child.child}
        )


class TestGetFirstLinkOccurenceUsingNode(SimpleTestCase):

    def setUp(self):
        self.tree = ProgramTreeFactory()
        self.child_reused = NodeGroupYearFactory()

    def test_when_child_not_used(self):
        LinkFactory(parent=self.tree.root_node)
        result = self.tree.get_first_link_occurence_using_node(self.child_reused)
        self.assertEqual(result, None)

    def test_when_child_used_only_one_time_in_tree(self):
        link1 = LinkFactory(parent=self.tree.root_node)
        link1_1 = LinkFactory(parent=link1.child, child=self.child_reused)
        result = self.tree.get_first_link_occurence_using_node(self.child_reused)
        self.assertEqual(result, link1_1)

    def test_with_child_reused_in_tree(self):
        link1 = LinkFactory(parent=self.tree.root_node)
        link1_1 = LinkFactory(parent=link1.child, child=self.child_reused)
        link2 = LinkFactory(parent=self.tree.root_node)
        link2_1 = LinkFactory(parent=link2.child, child=self.child_reused)
        link3 = LinkFactory(parent=self.tree.root_node)
        link3_1 = LinkFactory(parent=link3.child, child=self.child_reused)

        result = self.tree.get_first_link_occurence_using_node(self.child_reused)
        error_msg = "Must take the first occurence from the order displayed in the tree"
        self.assertEqual(result, link1_1, error_msg)
        self.assertNotEqual(result, link2_1, error_msg)
        self.assertNotEqual(result, link3_1, error_msg)


class TestGetGreaterBlockValue(SimpleTestCase):
    def test_when_tree_is_empty(self):
        tree = ProgramTreeFactory()
        self.assertEqual(0, tree.get_greater_block_value())

    def test_when_1_link_without_block_value(self):
        tree = ProgramTreeFactory()
        LinkFactory(parent=tree.root_node, block=None)
        self.assertEqual(0, tree.get_greater_block_value())

    def test_when_multiple_links_with_multiple_values(self):
        tree = ProgramTreeFactory()
        LinkFactory(parent=tree.root_node, block=13)
        LinkFactory(parent=tree.root_node, block=None)
        LinkFactory(parent=tree.root_node, block=1)
        LinkFactory(parent=tree.root_node, block=456)
        LinkFactory(parent=tree.root_node, block=123)
        self.assertEqual(6, tree.get_greater_block_value())


class TestCopyAndPrune(SimpleTestCase):

    def setUp(self):
        self.auth_relations = [AuthorizedRelationshipObjectFactory()]

        self.original_root = NodeGroupYearFactory()

        self.original_link = LinkFactory(parent=self.original_root, block=0)

        self.original_tree = ProgramTreeFactory(
            root_node=self.original_root,
            authorized_relationships=self.auth_relations
        )

    def test_should_copy_nodes(self):
        copied_tree = self.original_tree.prune()
        copied_root = copied_tree.root_node
        self.assertEqual(copied_root.node_id, self.original_root.node_id)
        self.assertEqual(copied_root.title, self.original_root.title)
        original_title = self.original_root.title
        copied_root.title = "Another value"
        self.assertEqual(copied_root.title, "Another value")
        self.assertEqual(self.original_root.title, original_title)

    def test_should_copy_tree(self):
        copied_tree = self.original_tree.prune()
        self.assertEqual(copied_tree.root_node, self.original_tree.root_node)
        self.assertEqual(copied_tree.authorized_relationships, self.original_tree.authorized_relationships)
        self.assertNotEqual(id(self.original_tree), id(copied_tree))

    def test_should_copy_links(self):
        original_link = self.original_tree.root_node.children[0]
        copied_tree = self.original_tree.prune()
        copied_link = copied_tree.root_node.children[0]
        self.assertEqual(copied_link.child, original_link.child)
        self.assertEqual(copied_link.parent, original_link.parent)
        self.assertEqual(copied_link.block, original_link.block)

        self.assertNotEqual(id(original_link), id(copied_link))
        self.assertNotEqual(id(original_link.child), id(copied_link.child))

        copied_link.block = 123456
        self.assertEqual(copied_link.block, 123456)
        self.assertNotEqual(original_link.block, 123456)

    def test_when_change_tree_signature(self):
        original_signature = ['self', 'root_node', 'authorized_relationships', 'entity_id', 'prerequisites']
        current_signature = list(inspect.signature(ProgramTree.__init__).parameters.keys())
        error_msg = "Please update the {} function to fit with new object signature.".format(ProgramTree.prune)
        self.assertEqual(original_signature, current_signature, error_msg)

    def test_pruning_with_param_ignore_children_from(self):
        link = LinkFactory(parent=self.original_root)
        copied_tree = self.original_tree.prune(ignore_children_from={link.parent.node_type})
        self.assertListEqual([], copied_tree.root_node.children)

    def test_pruning_multiple_levels_with_param_ignore_children_from(self):
        link_1 = LinkFactory(
            parent__node_type=TrainingType.BACHELOR,
            child__node_type=GroupType.MINOR_LIST_CHOICE
        )
        link1_1 = LinkFactory(parent=link_1.child, child__node_type=GroupType.SUB_GROUP)
        link1_1_1 = LinkFactory(parent=link1_1.child)
        link1_1_1_1 = LinkFactory(parent=link1_1_1.child)
        original_tree = ProgramTreeFactory(root_node=link_1.parent)
        copied_tree = original_tree.prune(ignore_children_from={GroupType.SUB_GROUP})
        result = copied_tree.get_all_links()
        copied_link_1_1_1 = copied_tree.root_node.children[0].child.children[0].child
        self.assertListEqual([], copied_link_1_1_1.children)
        self.assertNotIn(link1_1_1, result)
        self.assertNotIn(link1_1_1_1, result)


class TestGetNodeByCodeAndYearProgramTree(SimpleTestCase):
    def setUp(self):
        self.year = 2020
        link = LinkFactory(child=NodeGroupYearFactory(node_id=1, code='AAAA', year=self.year))
        self.root_node = link.parent
        self.subgroup_node = link.child

        link_with_learning_unit = LinkFactory(parent=self.root_node, child=NodeLearningUnitYearFactory(node_id=1,
                                                                                                       code='BBBB',
                                                                                                       year=self.year))
        self.learning_unit_node = link_with_learning_unit.child

        self.tree = ProgramTreeFactory(root_node=self.root_node)

    def test_should_return_None_when_no_node_present_with_corresponding_code_and_year(self):
        result = self.tree.get_node_by_code_and_year('bla', 2019)
        with self.subTest('Wrong code and year'):
            self.assertIsNone(result)

        result = self.tree.get_node_by_code_and_year('BBBB', 2019)
        with self.subTest('Wrong year, good code'):
            self.assertIsNone(result)

        result = self.tree.get_node_by_code_and_year('bla', 2020)
        with self.subTest('Wrong code, good year'):
            self.assertIsNone(result)

    def test_should_return_node_matching_specific_code_and_year(self):
        result = self.tree.get_node_by_code_and_year('BBBB', self.year)
        with self.subTest('Test for NodeLearningUnitYear'):
            self.assertEqual(
                result,
                self.learning_unit_node
            )

        result = self.tree.get_node_by_code_and_year('AAAA', self.year)
        with self.subTest('Test for NodeGroupYear'):
            self.assertEqual(
                result,
                self.subgroup_node
            )


class TestGetNodesThatHavePrerequisites(SimpleTestCase):

    def setUp(self) -> None:
        self.link_with_root = LinkFactory(parent__title='ROOT', child__title='child_ROOT')
        self.link_with_child = LinkFactory(
            parent=self.link_with_root.child,
            child=NodeLearningUnitYearFactory(common_title_fr="child__child__ROOT",
                                              year=self.link_with_root.parent.year),
        )
        self.tree = ProgramTreeFactory(root_node=self.link_with_root.parent)

    def test_when_tree_has_not_node_that_have_prerequisites(self):
        self.assertEqual(self.tree.get_nodes_that_have_prerequisites(), [])

    def test_when_tree_has_node_that_have_prerequisites(self):
        tree = copy.deepcopy(self.tree)
        node_having_prerequisite = self.link_with_child.child
        PrerequisitesFactory.produce_inside_tree(
            context_tree=tree,
            node_having_prerequisite=node_having_prerequisite.entity_id,
            nodes_that_are_prequisites=[NodeLearningUnitYearFactory()]
        )
        result = tree.get_nodes_that_have_prerequisites()
        self.assertEqual(result, [node_having_prerequisite])


class TestGetLink(SimpleTestCase):
    def setUp(self):
        self.tree = ProgramTreeFactory()
        self.root = self.tree.root_node
        self.link1 = LinkFactory(parent=self.root)
        self.link11 = LinkFactory(parent=self.link1.child, child=NodeLearningUnitYearFactory())
        self.link12 = LinkFactory(parent=self.link11.child)
        self.link2 = LinkFactory(parent=self.root, child=NodeLearningUnitYearFactory())

    def test_should_return_none_when_link_does_not_exist_for_parent_and_child_in_tree(self):
        result = self.tree.get_link(parent=self.root, child=self.link11.child)
        self.assertIsNone(result)

    def test_should_return_link_when_link_exists_for_parent_and_child_in_tree(self):
        result = self.tree.get_link(parent=self.link2.parent, child=self.link2.child)
        self.assertEqual(
            result,
            self.link2
        )


class TestGetCodesPermittedAsPrerequisite(SimpleTestCase):

    def setUp(self):
        self.tree = ProgramTreeFactory()

    def test_when_tree_contains_learning_units(self):
        link_with_learn_unit = LinkFactory(parent=self.tree.root_node, child=NodeLearningUnitYearFactory())
        link_with_group = LinkFactory(parent=self.tree.root_node, child=NodeGroupYearFactory())
        result = self.tree.get_nodes_permitted_as_prerequisite()
        expected_result = [link_with_learn_unit.child]
        self.assertListEqual(result, expected_result)
        self.assertNotIn(link_with_group.child, result)

    def test_when_tree_contains_only_groups(self):
        link_with_group1 = LinkFactory(parent=self.tree.root_node, child=NodeGroupYearFactory())
        link_with_group2 = LinkFactory(parent=self.tree.root_node, child=NodeGroupYearFactory())
        result = self.tree.get_nodes_permitted_as_prerequisite()
        expected_result = []
        self.assertListEqual(result, expected_result)

    def test_list_ordered_by_code(self):
        link_with_learn_unit1 = LinkFactory(parent=self.tree.root_node, child=NodeLearningUnitYearFactory(code='c2'))
        link_with_learn_unit2 = LinkFactory(parent=self.tree.root_node, child=NodeLearningUnitYearFactory(code='c1'))
        link_with_learn_unit3 = LinkFactory(parent=self.tree.root_node, child=NodeLearningUnitYearFactory(code='c3'))
        result = self.tree.get_nodes_permitted_as_prerequisite()
        expected_result_order = [link_with_learn_unit2.child, link_with_learn_unit1.child, link_with_learn_unit3.child]
        self.assertListEqual(result, expected_result_order)

    def test_when_node_is_used_inside_minor_and_inside_the_bachelor(self):
        tree = ProgramTreeFactory(root_node__node_type=TrainingType.BACHELOR)
        minor = NodeGroupYearFactory()
        ue = NodeLearningUnitYearFactory()

        LinkFactory(
            parent=tree.root_node,
            child=LinkFactory(
                parent=minor,
                child=ue
            ).parent
        )
        LinkFactory(parent=tree.root_node, child=ue)

        result = tree.get_nodes_permitted_as_prerequisite()
        expected_result = [ue]
        self.assertListEqual(result, expected_result)


class TestGetAllFinalities(SimpleTestCase):

    def setUp(self):
        self.tree = ProgramTreeFactory(root_node__node_type=TrainingType.PGRM_MASTER_120)
        self.finalities_group = NodeGroupYearFactory(node_type=GroupType.FINALITY_120_LIST_CHOICE)
        LinkFactory(parent=self.tree.root_node, child=self.finalities_group)

    def test_result_is_set_instance(self):
        msg = "Rsult chould be a set only for performance."
        self.assertIsInstance(self.tree.get_all_finalities(), set, msg)

    def test_when_contains_no_finalities(self):
        LinkFactory(parent=self.tree.root_node, child__node_type=GroupType.COMMON_CORE)
        self.assertSetEqual(self.tree.get_all_finalities(), set())

    def test_when_program_is_empty_but_root_is_finality(self):
        finality_tree = ProgramTreeFactory(root_node__node_type=TrainingType.MASTER_MD_120)
        self.assertSetEqual(finality_tree.get_all_finalities(), {finality_tree.root_node})

    def test_when_program_is_empty_and_root_is_not_finality(self):
        bachelor_tree = ProgramTreeFactory(root_node__node_type=TrainingType.BACHELOR)
        self.assertSetEqual(bachelor_tree.get_all_finalities(), set())

    def test_when_contains_master_ma_120(self):
        link = LinkFactory(
            parent=self.finalities_group,
            child=NodeGroupYearFactory(node_type=TrainingType.MASTER_MA_120)
        )
        expected_result = {
            link.child
        }
        self.assertSetEqual(self.tree.get_all_finalities(), expected_result)

    def test_when_contains_master_md_120(self):
        link = LinkFactory(
            parent=self.finalities_group,
            child=NodeGroupYearFactory(node_type=TrainingType.MASTER_MD_120)
        )
        expected_result = {
            link.child
        }
        self.assertSetEqual(self.tree.get_all_finalities(), expected_result)

    def test_when_contains_master_ms_120(self):
        link = LinkFactory(
            parent=self.finalities_group,
            child=NodeGroupYearFactory(node_type=TrainingType.MASTER_MS_120)
        )
        expected_result = {
            link.child
        }
        self.assertSetEqual(self.tree.get_all_finalities(), expected_result)

    def test_when_contains_master_ma_180_240(self):
        link = LinkFactory(
            parent=self.finalities_group,
            child=NodeGroupYearFactory(node_type=TrainingType.MASTER_MA_180_240)
        )
        expected_result = {
            link.child
        }
        self.assertSetEqual(self.tree.get_all_finalities(), expected_result)

    def test_when_contains_master_md_180_240(self):
        link = LinkFactory(
            parent=self.finalities_group,
            child=NodeGroupYearFactory(node_type=TrainingType.MASTER_MD_180_240)
        )
        expected_result = {
            link.child
        }
        self.assertSetEqual(self.tree.get_all_finalities(), expected_result)

    def test_when_contains_master_ms_180_240(self):
        link = LinkFactory(
            parent=self.finalities_group,
            child=NodeGroupYearFactory(node_type=TrainingType.MASTER_MS_180_240)
        )
        expected_result = {
            link.child
        }
        self.assertSetEqual(self.tree.get_all_finalities(), expected_result)

    def test_when_contains_multiple_finalities(self):
        link1 = LinkFactory(
            parent=self.finalities_group,
            child=NodeGroupYearFactory(node_type=TrainingType.MASTER_MA_120)
        )
        link2 = LinkFactory(
            parent=self.finalities_group,
            child=NodeGroupYearFactory(node_type=TrainingType.MASTER_MD_120)
        )
        link3 = LinkFactory(
            parent=self.finalities_group,
            child=NodeGroupYearFactory(node_type=TrainingType.MASTER_MS_120)
        )
        expected_result = {
            link1.child,
            link2.child,
            link3.child,
        }
        self.assertSetEqual(self.tree.get_all_finalities(), expected_result)


class TestDetachNode(SimpleTestCase):

    def setUp(self):
        self.success_message = BusinessValidationMessage("Success message", MessageLevel.SUCCESS)
        self.error_message = BusinessValidationMessage("Error message", MessageLevel.ERROR)

    def test_should_raise_exception_when_path_is_not_valid(self):
        tree = ProgramTreeFactory()
        LinkFactory(parent=tree.root_node)
        path_to_detach = "Invalid path"
        with self.assertRaises(osis_common.ddd.interface.BusinessExceptions):
            tree.detach_node(path_to_detach, mock.Mock(), mock.Mock())

    @patch.object(DetachNodeValidatorList, 'validate')
    def test_should_propagate_exception_when_validator_raises_exception(self, mock_validate):
        mock_validate.side_effect = osis_common.ddd.interface.BusinessExceptions(["error occured", "an other error"])

        tree = ProgramTreeFactory()
        link = LinkFactory(parent=tree.root_node)
        path_to_detach = build_path(link.parent, link.child)

        with self.assertRaises(osis_common.ddd.interface.BusinessExceptions) as exception_context:
            tree.detach_node(path_to_detach, mock.Mock(), mock.Mock())

        self.assertListEqual(
            exception_context.exception.messages,
            ["error occured", "an other error"]
        )


class TestGet2mOptionList(SimpleTestCase):

    def setUp(self):
        self.program_2m = NodeGroupYearFactory(node_type=TrainingType.PGRM_MASTER_120)
        self.finality_choice = NodeGroupYearFactory(node_type=GroupType.FINALITY_120_LIST_CHOICE)
        self.option_list_choice = NodeGroupYearFactory(node_type=GroupType.OPTION_LIST_CHOICE)

        LinkFactory(parent=self.program_2m, child=self.finality_choice)
        LinkFactory(parent=self.program_2m, child=self.option_list_choice)

        self.tree_2m = ProgramTreeFactory(root_node=self.program_2m)

    def test_when_option_is_inside_finality_120(self):
        LinkFactory(parent=self.finality_choice, child__node_type=MiniTrainingType.OPTION)
        self.assertSetEqual(self.tree_2m.get_2m_option_list(), set(), "Should not take options from finalities 120")

    def test_when_option_is_inside_finality_180(self):
        link = LinkFactory(parent=self.program_2m, child__node_type=GroupType.FINALITY_180_LIST_CHOICE)
        LinkFactory(parent=link.child, child__node_type=MiniTrainingType.OPTION)
        self.assertSetEqual(self.tree_2m.get_2m_option_list(), set(), "Should not take options from finalities 180")

    def test_when_option_is_child_of_2m(self):
        link = LinkFactory(parent=self.option_list_choice, child__node_type=MiniTrainingType.OPTION)
        expected_result = {link.child}
        assertion_msg = "Should take option (child) from option list choice in 2M master program."
        self.assertSetEqual(self.tree_2m.get_2m_option_list(), expected_result, assertion_msg)


class TestSetPrerequisite(SimpleTestCase, ValidatorPatcherMixin):
    def setUp(self):
        self.year = 2020
        self.tree = ProgramTreeFactory(root_node__year=self.year)
        self.link1 = LinkFactory(parent=self.tree.root_node, child=NodeLearningUnitYearFactory(year=self.year))
        LinkFactory(parent=self.tree.root_node, child=NodeLearningUnitYearFactory(code='LOSIS1452', year=self.year))
        LinkFactory(parent=self.tree.root_node, child=NodeLearningUnitYearFactory(code='MARC2589', year=self.year))

    def test_should_not_set_prerequisites_when_clean_is_not_valid(self):
        self.mock_validator(
            validators_by_business_action.UpdatePrerequisiteValidatorList,
            ["error_message_text"],
            level=MessageLevel.ERROR
        )
        self.tree.set_prerequisite("LOSIS1452 OU MARC2589", self.link1.child)
        self.assertTrue(len(self.tree.get_all_prerequisites()) == 0)

    def test_should_set_prerequisites_when_clean_is_valid(self):
        self.mock_validator(
            validators_by_business_action.UpdatePrerequisiteValidatorList,
            ["success_message_text"],
            level=MessageLevel.SUCCESS
        )
        self.tree.set_prerequisite("LOSIS1452 OU MARC2589", self.link1.child)
        self.assertTrue(len(self.tree.get_all_prerequisites()) == 1)


class TestUpdateLink(SimpleTestCase):
    def setUp(self) -> None:
        self.tree = ProgramTreeFactory()
        self.link1 = LinkFactory(parent=self.tree.root_node, child=NodeLearningUnitYearFactory())

    @mock.patch('program_management.ddd.domain.program_tree.validators_by_business_action.UpdateLinkValidatorList')
    def test_assert_validator_called(self, mock_update_link_validator_list):
        result = self.tree.update_link(
            str(self.tree.root_node.pk),
            child_id=self.link1.child.entity_id,
            relative_credits=1,
            access_condition=False,
            is_mandatory=True,
            block=123,
            link_type=None,
            comment="Comment",
            comment_english="Comment english"
        )
        self.assertTrue(mock_update_link_validator_list.called)
        self.assertIsInstance(result, Link)


class TestProgramTreeIsEmpty(SimpleTestCase):
    def test_should_return_true_when_root_node_has_no_children(self):
        empty_program_tree = ProgramTreeFactory()

        self.assertTrue(empty_program_tree.is_empty())

    def test_should_return_true_when_root_node_only_contains_mandatory_children(self):
        program_tree_with_only_mandatory_children = self.create_program_tree_with_only_mandatory_children()

        self.assertTrue(program_tree_with_only_mandatory_children.is_empty())

    def test_should_return_false_when_root_node_contains_not_mandatory_children(self):
        program_tree_with_non_mandatory_children = self.create_program_tree_with_non_mandatory_children()

        self.assertFalse(program_tree_with_non_mandatory_children.is_empty())

    def create_program_tree_with_non_mandatory_children(self):
        root_node = NodeGroupYearFactory()
        LinkFactory(parent=root_node)
        return ProgramTreeFactory(root_node=root_node)

    def create_program_tree_with_only_mandatory_children(self) -> 'ProgramTree':
        root_node = NodeGroupYearFactory()
        child_node = NodeGroupYearFactory()
        LinkFactory(parent=root_node, child=child_node)
        program_tree_with_only_mandatory_children = ProgramTreeFactory(
            root_node=root_node,
            authorized_relationships=AuthorizedRelationshipList([
                AuthorizedRelationshipObjectFactory(
                    parent_type=root_node.node_type,
                    child_type=child_node.node_type,
                    min_count_authorized=1,
                    max_count_authorized=1
                )
            ])
        )
        return program_tree_with_only_mandatory_children


class TestIsEmpty(SimpleTestCase):
    def test_assert_is_empty_case_contains_nothing(self):
        program_tree = ProgramTreeFactory(
            authorized_relationships=AuthorizedRelationshipList([
                AuthorizedRelationshipObjectFactory()
            ])
        )
        self.assertTrue(program_tree.is_empty())

    def test_assert_is_empty_case_contains_only_mandatory_child(self):
        root_node = NodeGroupYearFactory()
        child_node = NodeGroupYearFactory()
        LinkFactory(parent=root_node, child=child_node)

        auth_relation = AuthorizedRelationshipObjectFactory(
            parent_type=root_node.node_type,
            child_type=child_node.node_type,
            min_count_authorized=1,
            max_count_authorized=1
        )
        program_tree = ProgramTreeFactory(
            root_node=root_node,
            authorized_relationships=AuthorizedRelationshipList([auth_relation])
        )
        self.assertTrue(program_tree.is_empty())

    def test_assert_is_not_empty_case_contain_more_than_mandatory(self):
        """
        root_node
        |---child_node (Mandatory)
        |--- child_node_2
        """
        root_node = NodeGroupYearFactory()
        child_node = NodeGroupYearFactory()
        LinkFactory(parent=root_node, child=child_node)

        child_node_2 = NodeGroupYearFactory()
        LinkFactory(parent=root_node, child=child_node_2)

        auth_relation_child = AuthorizedRelationshipObjectFactory(
            parent_type=root_node.node_type,
            child_type=child_node.node_type,
            min_count_authorized=1,
            max_count_authorized=1
        )
        auth_relation_child_2 = AuthorizedRelationshipObjectFactory(
            parent_type=root_node.node_type,
            child_type=child_node_2.node_type,
            min_count_authorized=0,
            max_count_authorized=1
        )
        program_tree = ProgramTreeFactory(
            root_node=root_node,
            authorized_relationships=AuthorizedRelationshipList([auth_relation_child, auth_relation_child_2])
        )
        self.assertFalse(program_tree.is_empty())


class TestGetIndirectParents(SimpleTestCase):

    def setUp(self) -> None:
        self.program_tree = ProgramTreeFactory.produce_standard_2M_program_tree_with_one_finality(
            current_year=2020,
            end_year=2020
        )

    def test_when_child_node_not_in_tree(self):
        child_node = NodeLearningUnitYearFactory()
        result = self.program_tree.search_indirect_parents(child_node)
        expected_result = []
        self.assertEqual(result, expected_result)

    def test_when_child_node_is_himself_an_indirect_parent(self):
        indirect_parent = next(n for n in self.program_tree.get_all_nodes() if n.is_finality())
        result = self.program_tree.search_indirect_parents(indirect_parent)
        expected_result = [self.program_tree.root_node]
        self.assertEqual(result, expected_result, "The indirect parent of a finality is the master 2M")

    def test_when_child_node_has_one_indirect_parent(self):
        child_node = next(n for n in self.program_tree.get_all_nodes() if n.is_finality_list_choice())
        result = self.program_tree.search_indirect_parents(child_node)
        expected_result = [self.program_tree.root_node]
        self.assertEqual(result, expected_result, "The indirect parent of a finality list choice is the master 2M")

    def test_when_child_node_has_one_indirect_parent_which_has_one_indirect_parent(self):
        child_node = NodeLearningUnitYearFactory()
        tree = ProgramTreeFactory.produce_standard_2M_program_tree_with_one_finality(
            current_year=2020,
            end_year=2020
        )
        finality = next(n for n in tree.get_all_nodes() if n.is_finality())
        finality.add_child(child_node)
        result = tree.search_indirect_parents(child_node)
        expected_result = [finality]
        self.assertEqual(result, expected_result)
        self.assertNotIn(
            tree.root_node,
            expected_result,
            "Should not take the indirect parent (master 2M) of the first indirect parent (finality)"
        )

    def test_when_child_node_used_twice_in_tree_with_2_different_indirect_parent(self):
        child_node = NodeLearningUnitYearFactory()
        tree = ProgramTreeFactory.produce_standard_2M_program_tree_with_one_finality(
            current_year=2020,
            end_year=2020
        )
        finality = next(n for n in tree.get_all_nodes() if n.is_finality())
        finality.add_child(child_node)  # Indirect parent is finality
        common_core = next(n for n in tree.get_all_nodes() if n.is_common_core())
        common_core.add_child(child_node)  # Indirect parent is master 2M

        result = tree.search_indirect_parents(child_node)
        expected_result = [tree.root_node, finality]
        self.assertEqual(
            result,
            expected_result,
            "The learning unit Node is used in the common core (which is in the master 2M) AND in the finality"
        )
