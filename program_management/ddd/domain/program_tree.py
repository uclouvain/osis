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
import collections
import copy
import itertools
from collections import Counter
from typing import List, Set, Optional, Dict

import attr

from base.ddd.utils.converters import to_upper_case_converter
from base.models.authorized_relationship import AuthorizedRelationshipList
from base.models.enums.education_group_types import EducationGroupTypesEnum, TrainingType, GroupType
from base.models.enums.link_type import LinkTypes
from base.utils.cache import cached_result
from education_group.ddd.business_types import *
from osis_common.ddd import interface
from osis_common.decorators.deprecated import deprecated
from program_management.ddd import command
from program_management.ddd.business_types import *
from program_management.ddd.command import DO_NOT_OVERRIDE
from program_management.ddd.domain import prerequisite, exception
from program_management.ddd.domain.link import factory as link_factory
from program_management.ddd.domain.node import factory as node_factory, NodeIdentity, Node, NodeNotFoundException
from program_management.ddd.repositories import load_authorized_relationship
from program_management.ddd.validators import validators_by_business_action
from program_management.ddd.validators._path_validator import PathValidator
from program_management.models.enums import node_type
from program_management.models.enums.node_type import NodeType

PATH_SEPARATOR = '|'
Path = str  # Example : "root|node1|node2|child_leaf"


@attr.s(frozen=True, slots=True)
class ProgramTreeIdentity(interface.EntityIdentity):
    code = attr.ib(type=str, converter=to_upper_case_converter)
    year = attr.ib(type=int)


class ProgramTreeBuilder:

    def duplicate(
            self,
            duplicate_from: 'ProgramTree',
            override_end_year_to: int = DO_NOT_OVERRIDE,
            override_start_year_to: int = None
    ) -> 'ProgramTree':
        """
        Generates new program tree with new nodes and links based on attributes of 'duplicate_from' program tree.
        :param duplicate_from: The program tree from which are copied attributes in the new one.
        :param override_end_year_to: This param override the 'end year' of all nodes and links in the Tree.
        :param override_start_year_to: This param override the 'start year' of all nodes and links in the Tree.
        :return:
        """
        copied_root = self._duplicate_root_and_direct_children(
            duplicate_from,
            override_end_year_to=override_end_year_to,
            override_start_year_to=override_start_year_to
        )
        copied_tree = attr.evolve(  # Copy to new object
            duplicate_from,
            root_node=copied_root,
            entity_id=ProgramTreeIdentity(code=copied_root.code, year=copied_root.year),
        )
        return copied_tree

    def _duplicate_root_and_direct_children(
            self,
            program_tree: 'ProgramTree',
            override_end_year_to: int = DO_NOT_OVERRIDE,
            override_start_year_to: int = DO_NOT_OVERRIDE
    ) -> 'Node':
        copy_from_node = program_tree.root_node
        new_parent = node_factory.duplicate(
            copy_from_node,
            override_end_year_to=override_end_year_to,
            override_start_year_to=override_start_year_to
        )
        mandatory_children_types = program_tree.get_ordered_mandatory_children_types(program_tree.root_node)
        for copy_from_link in [n for n in copy_from_node.children if n.child.node_type in mandatory_children_types]:
            child_node = copy_from_link.child
            new_child = node_factory.duplicate(
                child_node,
                override_end_year_to=override_end_year_to,
                override_start_year_to=override_start_year_to
            )
            copied_link = link_factory.create_link(new_parent, new_child)
            new_parent.children.append(copied_link)
        return new_parent

    def copy_to_next_year(self, copy_from: 'ProgramTree', repository: 'ProgramTreeRepository') -> 'ProgramTree':
        validators_by_business_action.CopyProgramTreeValidatorList(copy_from).validate()
        identity_next_year = attr.evolve(copy_from.entity_id, year=copy_from.entity_id.year + 1)
        try:
            # Case update program tree to next year
            program_tree_next_year = repository.get(identity_next_year)
        except exception.ProgramTreeNotFoundException:
            # Case create program tree to next year
            root_next_year = node_factory.copy_to_next_year(copy_from.root_node)
            program_tree_next_year = ProgramTree(
                entity_id=identity_next_year,
                root_node=root_next_year,
                authorized_relationships=load_authorized_relationship.load()
            )

        root_next_year = program_tree_next_year.root_node
        mandatory_types = copy_from.get_ordered_mandatory_children_types(
            parent_node=root_next_year
        )
        children_current_year = copy_from.root_node.get_direct_children_as_nodes()
        for child_current_year in children_current_year:
            if child_current_year.node_type in mandatory_types:
                child_next_year = node_factory.copy_to_next_year(child_current_year)
                root_next_year.add_child(child_next_year, is_mandatory=True)
        return program_tree_next_year

    # Do not delete : will be usefull to copy content of a program tree to next year
    def _copy_node_and_children_to_next_year(self, copy_from_node: 'Node') -> 'Node':
        parent_next_year = node_factory.copy_to_next_year(copy_from_node)
        for copy_from_link in copy_from_node.children:
            child_node = copy_from_link.child
            child_next_year = self._copy_node_and_children_to_next_year(child_node)
            link_next_year = link_factory.copy_to_next_year(copy_from_link, parent_next_year, child_next_year)
            parent_next_year.children.append(link_next_year)
        return parent_next_year

    def build_from_orphan_group_as_root(
            self,
            orphan_group_as_root: 'Group',
            node_repository: 'NodeRepository'
    ) -> 'ProgramTree':
        root_node = node_repository.get(NodeIdentity(code=orphan_group_as_root.code, year=orphan_group_as_root.year))
        program_tree = ProgramTree(root_node=root_node, authorized_relationships=load_authorized_relationship.load())
        self._generate_mandatory_direct_children(program_tree=program_tree)
        return program_tree

    def _generate_mandatory_direct_children(
            self,
            program_tree: 'ProgramTree',
    ) -> List['Node']:
        children = []
        root_node = program_tree.root_node
        for child_type in program_tree.get_ordered_mandatory_children_types(program_tree.root_node):
            child = node_factory.generate_from_parent(parent_node=root_node, child_type=child_type)
            root_node.add_child(child, is_mandatory=True)
            children.append(child)
        return children


@attr.s(slots=True, hash=False, eq=False)
class ProgramTree(interface.RootEntity):

    root_node = attr.ib(type=Node)
    authorized_relationships = attr.ib(type=AuthorizedRelationshipList, factory=list)
    entity_id = attr.ib(type=ProgramTreeIdentity)  # FIXME :: pass entity_id as mandatory param !

    def is_empty(self, parent_node=None):
        parent_node = parent_node or self.root_node
        for child_node in parent_node.children_as_nodes:
            if not self.is_empty(parent_node=child_node):
                return False
            is_mandatory_children = child_node.node_type in self.authorized_relationships.\
                get_ordered_mandatory_children_types(parent_node.node_type) if self.authorized_relationships else []
            if not is_mandatory_children:
                return False
        return True

    @entity_id.default
    def _entity_id(self) -> 'ProgramTreeIdentity':
        return ProgramTreeIdentity(self.root_node.code, self.root_node.year)

    def is_master_2m(self):
        return self.root_node.is_master_2m()

    def is_root(self, node: 'Node'):
        return self.root_node == node

    def allows_learning_unit_child(self, node: 'Node') -> bool:
        try:
            return self.authorized_relationships.is_authorized(
                parent_type=node.node_type,
                child_type=NodeType.LEARNING_UNIT,
            )
        except AttributeError:
            return False

    def get_parents_using_node_with_respect_to_reference(self, child_node: 'Node') -> List['Node']:
        links = _links_from_root(self.root_node)

        def _get_parents(child_node: 'Node') -> List['Node']:
            result = []
            reference_links = [link_obj for link_obj in links
                               if link_obj.child == child_node and link_obj.is_reference()]
            for link_obj in reference_links:
                reference_parents = _get_parents(link_obj.parent)
                if reference_parents:
                    result.extend(reference_parents)
                else:
                    result.append(link_obj.parent)
            return result

        return _get_parents(child_node)

    def get_all_parents(self, child_node: 'Node') -> Set['Node']:
        paths_using_node = self.get_paths_from_node(child_node)
        return set(
            itertools.chain.from_iterable(self.get_parents(path) for path in paths_using_node)
        )

    def get_2m_option_list(self):  # TODO :: unit tests
        tree_without_finalities = self.prune(
            ignore_children_from={GroupType.FINALITY_120_LIST_CHOICE, GroupType.FINALITY_180_LIST_CHOICE}
        )
        return tree_without_finalities.root_node.get_option_list()

    def get_parents(self, path: Path) -> List['Node']:  # TODO :: unit tests
        result = []
        str_nodes = path.split(PATH_SEPARATOR)
        if len(str_nodes) > 1:
            str_nodes = str_nodes[:-1]
            path = PATH_SEPARATOR.join(str_nodes)
            result.append(self.get_node(path))
            result += self.get_parents(PATH_SEPARATOR.join(str_nodes))
        return result

    def search_links_using_node(self, child_node: 'Node') -> List['Link']:
        return [link_obj for link_obj in self.get_all_links() if link_obj.child == child_node]

    def get_first_link_occurence_using_node(self, child_node: 'Node') -> 'Link':
        links = self.search_links_using_node(child_node)
        if links:
            return links[0]

    def get_node(self, path: Path) -> 'Node':
        """
        Return the corresponding node based on path of tree
        :param path: str
        :return: Node
        """

        def _get_node(root_node: 'Node', path: 'Path') -> 'Node':
            direct_child_id, separator, remaining_path = path.partition(PATH_SEPARATOR)
            direct_child = next(child for child in root_node.children_as_nodes if str(child.pk) == direct_child_id)

            if not remaining_path:
                return direct_child
            return _get_node(direct_child, remaining_path)

        try:
            if path == str(self.root_node.pk):
                return self.root_node
            return _get_node(self.root_node, path.split(PATH_SEPARATOR, maxsplit=1)[1])
        except (StopIteration, IndexError):
            raise NodeNotFoundException

    @deprecated  # Please use :py:meth:`~program_management.ddd.domain.program_tree.ProgramTree.get_node` instead !
    def get_node_by_id_and_type(self, node_id: int, node_type: NodeType) -> 'Node':
        """
        DEPRECATED :: Please use the :py:meth:`get_node <ProgramTree.get_node>` instead !
        Return the corresponding node based on the node_id value with respect to the class.
        :param node_id: int
        :param node_type: NodeType
        :return: Node
        """
        return next(
            (
                node for node in self.get_all_nodes()
                if node.node_id == node_id and node.type == node_type
            ),
            None
        )

    def get_node_smallest_ordered_path(self, node: 'Node') -> Optional[Path]:
        """
        Return the smallest ordered path of node inside the tree.
        The smallest ordered path would be the result of a depth-first
        search of the path of the node with respect to the order of the links.
        Meaning we will recursively search for the path node by searching
        first in the descendants of the first child and so on.
        :param node: Node
        :return: A Path if node is present in tree. None if not.
        """
        if node == self.root_node:
            return build_path(self.root_node)

        return next(
            (path for path, node_obj in self.root_node.descendents if node_obj == node),
            None
        )

    def get_node_by_code_and_year(self, code: str, year: int) -> 'Node':
        """
        Return the corresponding node based on the code and year.
        :param code: str
        :param year: int
        :return: Node
        """
        return next(
            (
                node for node in self.get_all_nodes()
                if node.code == code and node.academic_year.year == year
            ),
            None
        )

    def get_all_nodes(self, types: Set[EducationGroupTypesEnum] = None) -> Set['Node']:
        """
        Return a flat set of all nodes present in the tree
        :return: list of Node
        """
        all_nodes = set([self.root_node] + _nodes_from_root(self.root_node))
        if types:
            return set(n for n in all_nodes if n.node_type in types)
        return all_nodes

    def get_all_learning_unit_nodes(self) -> List['NodeLearningUnitYear']:
        return self.root_node.get_all_children_as_learning_unit_nodes()

    def get_nodes_by_type(self, node_type_value) -> Set['Node']:
        return {node for node in self.get_all_nodes() if node.type == node_type_value}

    def get_nodes_that_have_prerequisites(self) -> List['NodeLearningUnitYear']:
        return list(
            sorted(
                (
                    node_obj for node_obj in self.get_nodes_by_type(node_type.NodeType.LEARNING_UNIT)
                    if node_obj.has_prerequisite
                ),
                key=lambda node_obj: node_obj.code
            )
        )

    def get_codes_permitted_as_prerequisite(self) -> List[str]:
        learning_unit_nodes_contained_in_program = self.get_nodes_by_type(node_type.NodeType.LEARNING_UNIT)
        return list(sorted(node_obj.code for node_obj in learning_unit_nodes_contained_in_program))

    def get_nodes_that_are_prerequisites(self) -> List['NodeLearningUnitYear']:  # TODO :: unit test
        return list(
            sorted(
                (
                    node_obj for node_obj in self.get_all_nodes()
                    if node_obj.is_learning_unit() and node_obj.is_prerequisite
                ),
                key=lambda node_obj: node_obj.code
            )
        )

    def count_usage(self, node: 'Node') -> int:
        return Counter(_nodes_from_root(self.root_node))[node]

    def get_all_finalities(self) -> Set['Node']:
        finality_types = set(TrainingType.finality_types_enum())
        return self.get_all_nodes(types=finality_types)

    def get_greater_block_value(self) -> int:
        all_links = self.get_all_links()
        if not all_links:
            return 0
        return max(link_obj.block_max_value for link_obj in all_links)

    def get_all_links(self) -> List['Link']:
        return _links_from_root(self.root_node)

    def _links_mapped_by_child_and_parent(self) -> Dict:
        return {
                str(link.child.entity_id) + str(link.parent.entity_id): link
                for link in self.get_all_links()
        }

    def get_link(self, parent: 'Node', child: 'Node') -> 'Link':
        my_map = self._links_mapped_by_child_and_parent()
        return my_map.get(str(child.entity_id) + str(parent.entity_id))

    def prune(self, ignore_children_from: Set[EducationGroupTypesEnum] = None) -> 'ProgramTree':
        copied_root_node = _copy(self.root_node, ignore_children_from=ignore_children_from)
        return ProgramTree(root_node=copied_root_node, authorized_relationships=self.authorized_relationships)

    def get_ordered_mandatory_children_types(self, parent_node: 'Node') -> List[EducationGroupTypesEnum]:
        return self.authorized_relationships.get_ordered_mandatory_children_types(parent_node.node_type)

    def paste_node(
            self,
            node_to_paste: 'Node',
            paste_command: command.PasteElementCommand,
            tree_repository: 'ProgramTreeRepository',
            tree_version_repository: 'ProgramTreeVersionRepository'
    ) -> 'Link':
        """
        Add a node to the tree
        :param node_to_paste: Node to paste into the tree
        :param paste_command: a paste node command
        :param tree_repository: a tree repository
        :return: the created link
        """
        path_to_paste_to = paste_command.path_where_to_paste
        node_to_paste_to = self.get_node(path_to_paste_to)
        if node_to_paste_to.is_minor_major_list_choice() and node_to_paste.is_minor_major_deepening():
            link_type = LinkTypes.REFERENCE
        else:
            link_type = LinkTypes[paste_command.link_type] if paste_command.link_type else None

        validator = validators_by_business_action.PasteNodeValidatorList(
            self,
            node_to_paste,
            paste_command,
            link_type,
            tree_repository,
            tree_version_repository
        )
        validator.validate()

        return node_to_paste_to.add_child(
            node_to_paste,
            access_condition=paste_command.access_condition,
            is_mandatory=paste_command.is_mandatory,
            block=paste_command.block,
            link_type=link_type,
            comment=paste_command.comment,
            comment_english=paste_command.comment_english,
            relative_credits=paste_command.relative_credits
        )

    def set_prerequisite(
            self,
            prerequisite_expression: 'PrerequisiteExpression',
            node: 'NodeLearningUnitYear'
    ) -> List['BusinessValidationMessage']:
        """
        Set prerequisite for the node corresponding to the path.
        """
        is_valid, messages = self.clean_set_prerequisite(prerequisite_expression, node)
        if is_valid:
            node.set_prerequisite(
                prerequisite.factory.from_expression(prerequisite_expression, self.root_node.year)
            )
        return messages

    def clean_set_prerequisite(
            self,
            prerequisite_expression: 'PrerequisiteExpression',
            node: 'NodeLearningUnitYear'
    ) -> (bool, List['BusinessValidationMessage']):
        validator = validators_by_business_action.UpdatePrerequisiteValidatorList(prerequisite_expression, node, self)
        return validator.is_valid(), validator.messages

    def get_remaining_children_after_detach(self, path_node_to_detach: 'Path'):
        children_with_counter = self.root_node.get_all_children_with_counter()
        children_with_counter.update([self.root_node])

        node_to_detach = self.get_node(path_node_to_detach)
        nodes_detached = node_to_detach.get_all_children_with_counter()
        nodes_detached.update([node_to_detach])
        children_with_counter.subtract(nodes_detached)

        return {node_obj for node_obj, number in children_with_counter.items() if number > 0}

    def detach_node(self, path_to_node_to_detach: Path, tree_repository: 'ProgramTreeRepository') -> 'Link':
        """
        Detach a node from tree
        :param path_to_node_to_detach: The path node to detach
        :param tree_repository: a tree repository
        :return: the suppressed link
        """
        PathValidator(path_to_node_to_detach).validate()

        node_to_detach = self.get_node(path_to_node_to_detach)
        parent_path, *__ = path_to_node_to_detach.rsplit(PATH_SEPARATOR, 1)
        parent = self.get_node(parent_path)
        validators_by_business_action.DetachNodeValidatorList(
            self,
            node_to_detach,
            parent_path,
            tree_repository
        ).validate()

        return parent.detach_child(node_to_detach)

    def __copy__(self) -> 'ProgramTree':
        return ProgramTree(
            root_node=_copy(self.root_node),
            authorized_relationships=copy.copy(self.authorized_relationships)
        )

    def get_relative_credits_values(self, child_node: 'NodeIdentity'):
        distinct_credits_repr = []
        node = self.get_node_by_code_and_year(child_node.code, child_node.year)

        for link_obj in self.search_links_using_node(node):
            if link_obj.relative_credits_repr not in distinct_credits_repr:
                distinct_credits_repr.append(link_obj.relative_credits_repr)
        return " ; ".join(
            set(["{}".format(credits) for credits in distinct_credits_repr])
        )

    def get_blocks_values(self, child_node: 'NodeIdentity'):
        node = self.get_node_by_code_and_year(child_node.code, child_node.year)
        return " ; ".join(
            [str(grp.block) for grp in self.search_links_using_node(node) if grp.block]
        )

    def is_empty(self):
        """
        Check if tree is empty.
        An empty tree is defined as a tree with other link than mandatory groups
        """
        nodes = self.get_all_nodes()
        for node in nodes:
            counter_direct_children = Counter(node.get_children_types(include_nodes_used_as_reference=True))
            counter_mandatory_direct_children = Counter(self.get_ordered_mandatory_children_types(node))

            if counter_direct_children - counter_mandatory_direct_children:
                return False
        return True

    def update_link(
            self,
            parent_path: Path,
            child_id: 'NodeIdentity',
            relative_credits: int,
            access_condition: bool,
            is_mandatory: bool,
            block: int,
            link_type: str,
            comment: str,
            comment_english: str
    ) -> 'Link':
        """
        Update link's attributes between parent_path and child_node
        :param parent_path: The parent path node
        :param child_id: The identity of child node
        :param relative_credits: The link's relative credits
        :param access_condition: The link's access_condition
        :param is_mandatory: The link's is_mandatory
        :param block: The block of link
        :param link_type: The type of link
        :param comment: The comment of link
        :param comment_english: The comment english of link
        :return: Updated link
        """
        parent_node = self.get_node(parent_path)
        child_node = parent_node.get_direct_child_as_node(child_id)

        link_updated = parent_node.update_link_of_direct_child_node(
            child_id,
            relative_credits=relative_credits,
            access_condition=access_condition,
            is_mandatory=is_mandatory,
            block=block,
            link_type=link_type,
            comment=comment,
            comment_english=comment_english
        )

        validators_by_business_action.UpdateLinkValidatorList(
            self,
            child_node,
            link_updated
        ).validate()
        return link_updated

    @cached_result
    def _paths_by_node(self) -> Dict['Node', List['Path']]:
        paths_by_node = collections.defaultdict(list)
        for path, child_node in self.root_node.descendents:
            paths_by_node[child_node].append(path)
        return paths_by_node

    # TODO : to rename into "search_paths_using_node"
    def get_paths_from_node(self, node: 'Node') -> List['Path']:
        return self._paths_by_node().get(node) or []

    def search_indirect_parents(self, node: 'Node') -> List['NodeGroupYear']:
        paths = self.get_paths_from_node(node)
        indirect_parents = []
        for path in paths:
            for parent in self.get_parents(path):
                if parent.is_indirect_parent() and node != parent:
                    indirect_parents.append(parent)
                    break
        return indirect_parents

    def contains(self, node: Node) -> bool:
        return node in self.get_all_nodes()


def _nodes_from_root(root: 'Node') -> List['Node']:
    nodes = [root]
    for link in root.children:
        nodes.extend(_nodes_from_root(link.child))
    return nodes


def _links_from_root(root: 'Node', ignore: Set[EducationGroupTypesEnum] = None) -> List['Link']:
    links = []
    for link in root.children:
        if not ignore or link.parent.node_type not in ignore:
            links.append(link)
            links.extend(_links_from_root(link.child, ignore=ignore))
    return links


def build_path(*nodes):
    return '{}'.format(PATH_SEPARATOR).join((str(n.node_id) for n in nodes))


def _copy(root: 'Node', ignore_children_from: Set[EducationGroupTypesEnum] = None):
    new_node = node_factory.deepcopy_node_without_copy_children_recursively(root)
    new_children = []
    for link in root.children:
        if ignore_children_from and link.parent.node_type in ignore_children_from:
            continue
        new_child = _copy(link.child, ignore_children_from=ignore_children_from)
        new_link = link_factory.deepcopy_link_without_copy_children_recursively(link)
        new_link.child = new_child
        new_children.append(new_link)
    new_node.children = new_children
    return new_node


def _path_contains(path: 'Path', node: 'Node') -> bool:
    return PATH_SEPARATOR + str(node.pk) in path
