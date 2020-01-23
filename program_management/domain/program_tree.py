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
from program_management.domain import node


class ProgramTree:
    def __init__(self, root_node: node.Node):
        if not isinstance(root_node, node.Node):
            raise Exception('root_group args must be an instance of Node')
        self.root_node = root_node

    def get_node(self, path: str) -> node.Node:
        """
        Return the corresponding node based on identifier (path) generated at instantiate of tree
        :param path: str
        :return: Node
        """
        try:
            return next(n for n in self.get_all_nodes() if n.path == path)
        except StopIteration:
            raise node.NodeNotFoundException

    def get_all_nodes(self):
        """
        Return a flat list of all nodes which are in the tree
        :return: list of Node
        """
        return [self.root_node] + _nodes_from_root(self.root_node)

    def add_node(self, node: node.Node, path: str = None, **kwargs):
        """
        Add a node to the tree
        :param node: Node to add on the tree
        :param path: [Optional] The position where the node must be added
        """
        parent = self.get_node(path) if path else self.root_node
        parent.add_child(node, **kwargs)


def _nodes_from_root(root: node.Node):
    nodes = [root]
    for link in root.children:
        nodes.extend(_nodes_from_root(link.child))
    return nodes
