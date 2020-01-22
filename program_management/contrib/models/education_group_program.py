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
from program_management.contrib.models.node import Node


class EducationGroupProgram:
    def __init__(self, root_group: Node):
        if not isinstance(root_group, Node):
            raise Exception('root_group args must be an instance of Node')
        self.root_group = root_group

    def save(self):
        if self.root_group is not None:
            self._save_children(self.root_group)

    def _save_children(self, node: Node):
        for link in node.children:
            self._save_children(link.child)
            link.save()

    def get_node(self, path: str) -> Node:
        """
        Return the corresponding node based on identifier (path) generated at instantiate of tree
        :param path: str
        :return: Node
        """
        try:
            return next(node for node in self.get_all_nodes() if node.path == path)
        except StopIteration:
            raise NodeNotFoundException

    def get_all_nodes(self):
        """
        Return a flat list of all nodes which are in the tree
        :return: list of Node
        """
        return [self.root_group] + nodes_from_root(self.root_group)

    def add_node(self, node: Node, path: str = None, **kwargs):
        """
        Add a node to the tree
        :param node: Node to add on the tree
        :param path: [Optional] The position where the node must be added
        """
        parent = self.get_node(path) if path else self.root_group
        parent.add_child(node, **kwargs)


def nodes_from_root(root: Node):
    nodes = [root]
    for link in root.children:
        nodes.extend(nodes_from_root(link.child))
    return nodes


class NodeNotFoundException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__("The node cannot be found on the current tree")
