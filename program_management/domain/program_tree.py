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
from program_management.contrib.validation import BusinessValidator
from program_management.domain import node


class AddNodeValidator(BusinessValidator):
    tree: ProgramTree = None
    node_to_add: node.Node = None
    where_to_add: str = None

    def __init__(self, tree: ProgramTree, node_to_add: Node, where_to_add: str):
        super(AddNodeValidator, self).__init__()
        self.tree = tree
        self.node_to_add = node_to_add
        self.where_to_add = where_to_add


class AuthorizedRelationshipValidator(AddNodeValidator):
    pass  # Implements rules based on AuthorizedRelationhips


class AddOptionsValidator(AddNodeValidator):
    pass  # cf. _check_attach_options_rules


class AddFinalityEndDateValidator(AddNodeValidator):
    pass  # cf. _check_end_year_constraints_on_2m


class NodeDuplicationValidator(AddNodeValidator):
    pass  # cf. _check_new_attach_is_not_duplication


class AddGroupYearNodeValidator(BusinessValidator):
    validators = [
        AuthorizedRelationshipValidator,
        AddOptionsValidator,
        AddFinalityEndDateValidator,
        NodeDuplicationValidator,
    ]


class AddLearningUnitYearNodeValidator(BusinessValidator):
    validators = [
        #     ...
    ]


class AddNodeValidatorFactory:
    def get_add_node_validator(self, tree: ProgramTree, node_to_add: node.Node, where_to_add: str):
        add_node_validator_class = {
            node.NodeEducationGroupYear: AddGroupYearNodeValidator,
            node.NodeGroupYear: AddGroupYearNodeValidator,
            node.NodeLearningUnitYear: AddLearningUnitYearNodeValidator,
            # node.NodeLearningClassYear: ???,
        }[node_to_add.__class__]
        return add_node_validator_class(tree, node_to_add, where_to_add)


factory = AddNodeValidatorFactory()


class ProgramTree:
    def __init__(self, root_node: node.Node):
        if not isinstance(root_node, node.Node):
            raise Exception('root_group args must be an instance of Node')
        self.root_node = root_node

    def get_node(self, path: str) -> node.Node:
        """
        Return the corresponding node based on path of tree
        :param path: str
        :return: Node
        """
        try:
            return {
                str(self.root_node.pk): self.root_node,
                **self.root_node.descendents
            }[path]
        except KeyError:
            raise node.NodeNotFoundException

    def get_all_nodes(self):
        """
        Return a flat list of all nodes which are in the tree
        :return: list of Node
        """
        return [self.root_node] + _nodes_from_root(self.root_node)

    def attach_node(self, node: node.Node, path: str = None, **kwargs):
        """
        Add a node to the tree
        :param node: Node to add on the tree
        :param path: [Optional] The position where the node must be added
        """
        parent = self.get_node(path) if path else self.root_node
        factory.get_add_node_validator(self, node, path)
        parent.add_child(node, **kwargs)

    def detach_node(self, path: str):
        """
        Detach a node from tree
        :param path: The path node to detach
        :return:
        """
        parent_path, *node_id = path.rsplit('|', 1)
        parent = self.get_node(parent_path)
        if not node_id:
            raise Exception("You cannot detach root node")
        parent.detach_child(node_id)


def _nodes_from_root(root: node.Node):
    nodes = [root]
    for link in root.children:
        nodes.extend(_nodes_from_root(link.child))
    return nodes
