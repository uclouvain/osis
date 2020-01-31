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
from program_management.domain import node
from program_management.models.enums.node_type import NodeType


class LinkFactory:
    def get_link(self, parent: node.Node, child: node.Node, **kwargs):
        if parent.type == NodeType.LEARNING_UNIT.name:
            return LinkWithChildLeaf(parent, child, **kwargs)
        else:
            return LinkWithChildBranch(parent, child, **kwargs)


factory = LinkFactory()


class Link:

    parent: node.Node = None
    child: node.Node = None
    relative_credits: int = None
    min_credits: int = None
    max_credits: int = None
    is_mandatory: int = None
    block: str = None
    access_condition = None  # TODO :: typing
    comment: str = None
    comment_english: str = None
    own_comment: str = None
    quadrimester_derogation = None  # TODO :: typing
    link_type: LinkTypes = None  # TODO :: Move Enum from model to business

    def __init__(self, parent: node.Node, child: node.Node, **kwargs):
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
    def __init__(self, parent: node.Node, child: node.Node, **kwargs):
        super(LinkWithChildLeaf, self).__init__(parent, child, **kwargs)


class LinkWithChildBranch(Link):
    pass
