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
from program_management.DomainDrivenDesign.domain import node
from program_management.DomainDrivenDesign.domain.authorized_relationship import AuthorizedRelationshipList


class ProgramTree:

    root_node = None
    authorized_relationships = None

    def __init__(self, root_node: node.Node, authorized_relationships: AuthorizedRelationshipList = None):
        if not isinstance(root_node, node.Node):
            raise Exception('root_group args must be an instance of Node')
        self.root_node = root_node
        self.authorized_relationships = authorized_relationships or []

    def __eq__(self, other):
        return self.root_node == other.root_node

    # TODO :: typer "path" (pour plus de lisibilité dans le code)
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
        # Avoid circular import
        from program_management.DomainDrivenDesign.domain.tree.validators.attach_node import factory as attach_node_validator_factory
        parent = self.get_node(path) if path else self.root_node
        validator = attach_node_validator_factory.get_attach_node_validator(self, node, path)
        validator.validate()
        if validator.is_valid():
            parent.add_child(node, **kwargs)
        else:
            return validator.error_messages

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
