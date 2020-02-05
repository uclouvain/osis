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
from base.models.enums.link_type import LinkTypes
from education_group.enums.node_type import NodeType


class Link:

    # TODO :: Typing for Node (cyclic import)
    # Solution 1 : if TYPE_CHECKING: from program_management.domain.node import Node + replace Node -> 'Node'
    # Solution 2 : Node = TypeVar("Node", bound="program_management.domain.node.Node")
    # Solution 3 : Node = TypeAlias('program_management.domain.node.Node')  # must be fully qualified name?
    # Solution 4 : creates an interface used by Node and Link
    parent = None
    child = None
    relative_credits = None
    min_credits = None
    max_credits = None
    is_mandatory = None
    block = None
    access_condition = None  # TODO :: typing
    comment = None
    comment_english = None
    own_comment = None
    quadrimester_derogation = None  # TODO :: typing
    link_type = None  # TODO :: Move Enum from model to business

    def __init__(self, parent, child, **kwargs):
        self.parent = parent
        self.child = child
        self.relative_credits = kwargs.get('relative_credits')
        self.min_credits = kwargs.get('min_credits')
        self.max_credits = kwargs.get('max_credits')
        self.is_mandatory = kwargs.get('is_mandatory') or False
        self.block = kwargs.get('block')
        self.access_condition = kwargs.get('access_condition') or False
        self.comment = kwargs.get('comment')
        self.comment_english = kwargs.get('comment_english')
        self.own_comment = kwargs.get('own_comment')
        self.quadrimester_derogation = kwargs.get('quadrimester_derogation')
        self.link_type = kwargs.get('link_type')


class LinkWithChildLeaf(Link):
    def __init__(self, *args, **kwargs):
        super(LinkWithChildLeaf, self).__init__(*args, **kwargs)


class LinkWithChildBranch(Link):
    pass


class LinkFactory:

    def get_link(self, parent, child, **kwargs) -> Link:
        if parent and parent.node_type == NodeType.LEARNING_UNIT:
            return LinkWithChildLeaf(parent, child, **kwargs)
        else:
            return LinkWithChildBranch(parent, child, **kwargs)


factory = LinkFactory()
