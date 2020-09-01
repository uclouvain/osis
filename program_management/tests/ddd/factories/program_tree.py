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
import factory.fuzzy

from base.models.authorized_relationship import AuthorizedRelationshipList
from base.models.enums.education_group_types import GroupType, TrainingType
from program_management.ddd.domain.program_tree import ProgramTree, ProgramTreeIdentity
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeGroupYearFactory


class ProgramTreeIdentityFactory(factory.Factory):

    class Meta:
        model = ProgramTreeIdentity
        abstract = False

    code = factory.Sequence(lambda n: 'Code%02d' % n)
    year = factory.fuzzy.FuzzyInteger(low=1999, high=2099)


class ProgramTreeFactory(factory.Factory):

    class Meta:
        model = ProgramTree
        abstract = False

    root_node = factory.SubFactory(NodeGroupYearFactory)
    authorized_relationships = AuthorizedRelationshipList([])
    entity_id = factory.SubFactory(
        ProgramTreeIdentityFactory,
        code=factory.SelfAttribute("..root_node.code"),
        year=factory.SelfAttribute("..root_node.year")
    )

    @staticmethod
    def produce_standard_2M_program_tree(current_year: int, end_year: int) -> 'ProgramTree':
        """Creates a 2M standard version"""

        tree_standard = ProgramTreeFactory(
            root_node__node_type=TrainingType.PGRM_MASTER_120,
            root_node__end_year=end_year,
            root_node__year=current_year,
        )
        link1 = LinkFactory(
            parent=tree_standard.root_node,
            child__node_type=GroupType.COMMON_CORE,
            child__end_year=end_year,
            child__year=current_year,
        )
        link2 = LinkFactory(
            parent=tree_standard.root_node,
            child__node_type=GroupType.FINALITY_120_LIST_CHOICE,
            child__end_year=end_year,
            child__year=current_year,
        )
        link3 = LinkFactory(
            parent=tree_standard.root_node,
            child__node_type=GroupType.OPTION_LIST_CHOICE,
            child__end_year=end_year,
            child__year=current_year,
        )
        tree_standard.root_node.children = [link1, link2, link3]

        return tree_standard
