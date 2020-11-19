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

from program_management.ddd.domain.program_tree_version import ProgramTreeVersion, ProgramTreeVersionIdentity
from program_management.ddd.repositories.program_tree import ProgramTreeRepository
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory


class ProgramTreeVersionIdentityFactory(factory.Factory):

    class Meta:
        model = ProgramTreeVersionIdentity
        abstract = False

    offer_acronym = factory.Sequence(lambda n: 'OFFERACRONYM%02d' % n)
    year = factory.fuzzy.FuzzyInteger(low=1999, high=2099)
    version_name = factory.Sequence(lambda n: 'VERSION%02d' % n)
    is_transition = False


class ProgramTreeVersionFactory(factory.Factory):

    class Meta:
        model = ProgramTreeVersion
        abstract = False

    tree = factory.SubFactory(ProgramTreeFactory)
    program_tree_identity = factory.SelfAttribute("tree.entity_id")
    program_tree_repository = ProgramTreeRepository()
    start_year = factory.SelfAttribute("tree.root_node.start_year")
    entity_id = factory.SubFactory(
        ProgramTreeVersionIdentityFactory,
        offer_acronym=factory.SelfAttribute("..tree.root_node.title"),
        year=factory.SelfAttribute("..tree.root_node.year")
    )
    entity_identity = factory.SelfAttribute("entity_id")
    version_name = factory.SelfAttribute("entity_id.version_name")
    end_year_of_existence = factory.SelfAttribute("tree.root_node.end_year")

    @staticmethod
    def produce_standard_2M_program_tree(current_year: int, end_year: int) -> 'ProgramTreeVersion':
        """Creates a 2M standard version"""
        tree_standard = ProgramTreeFactory.produce_standard_2M_program_tree(current_year, end_year)

        return ProgramTreeVersionFactory(
            tree=tree_standard,
            entity_id__year=current_year,
            program_tree_identity=tree_standard.entity_id,
        )


class StandardProgramTreeVersionFactory(ProgramTreeVersionFactory):
    entity_id = factory.SubFactory(
        ProgramTreeVersionIdentityFactory,
        offer_acronym=factory.SelfAttribute("..tree.root_node.title"),
        year=factory.SelfAttribute("..tree.root_node.year"),
        version_name=""
    )


class SpecificProgramTreeVersionFactory(ProgramTreeVersionFactory):
    entity_id = factory.SubFactory(
        ProgramTreeVersionIdentityFactory,
        offer_acronym=factory.SelfAttribute("..tree.root_node.title"),
        year=factory.SelfAttribute("..tree.root_node.year"),
        version_name="SPECIFIC"
    )
