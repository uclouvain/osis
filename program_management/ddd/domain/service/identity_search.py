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
import functools
import itertools
import operator
from typing import Union, List

from django.db.models import F, Subquery, Q

from program_management.ddd.business_types import *

from base.models.enums.education_group_types import MiniTrainingType, TrainingType
from education_group.ddd.domain.group import GroupIdentity
from education_group.ddd.domain.mini_training import MiniTrainingIdentity
from education_group.ddd.domain.training import TrainingIdentity
from education_group.models.group_year import GroupYear
from osis_common.ddd import interface
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.domain.program_tree import ProgramTreeIdentity
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity, STANDARD
from education_group.ddd.domain.service.identity_search import TrainingIdentitySearch \
    as EducationGroupTrainingIdentitySearch
from program_management.models.education_group_version import EducationGroupVersion


class ProgramTreeVersionIdentitySearch(interface.DomainService):

    @classmethod
    def get_from_node_identity(cls, node_identity: 'NodeIdentity') -> 'ProgramTreeVersionIdentity':
        return cls.get_from_node_identities([node_identity])[0]

    @classmethod
    def get_from_node_identities(cls, node_identities: List['NodeIdentity']) -> List['ProgramTreeVersionIdentity']:
        if not node_identities:
            return []

        filter_clause = functools.reduce(
            operator.or_,
            ((Q(partial_acronym=entity_id.code) & Q(academic_year__year=entity_id.year))
             for entity_id in node_identities)
        )
        values = GroupYear.objects.filter(
            filter_clause
        ).annotate(
            offer_acronym=F('educationgroupversion__offer__acronym'),
            year=F('academic_year__year'),
            version_name=F('educationgroupversion__version_name'),
            is_transition=F('educationgroupversion__is_transition'),
        ).values('offer_acronym', 'year', 'version_name', 'is_transition')
        if values:
            return [ProgramTreeVersionIdentity(**value) for value in values]
        raise interface.BusinessException("Program tree version identity not found")

    @classmethod
    def get_from_program_tree_identity(cls, identity: 'ProgramTreeIdentity') -> 'ProgramTreeVersionIdentity':
        return cls.get_from_node_identity(NodeIdentitySearch().get_from_program_tree_identity(identity))

    @classmethod
    def get_from_group_identity(cls, identity: 'GroupIdentity') -> 'ProgramTreeVersionIdentity':
        tree_identity = ProgramTreeIdentitySearch().get_from_group_identity(identity)
        return cls.get_from_program_tree_identity(tree_identity)

    @classmethod
    def get_all_program_tree_version_identities(
            cls,
            program_tree_version_identity: 'ProgramTreeVersionIdentity'
    ) -> List['ProgramTreeVersionIdentity']:
        """
            Return all program tree version identity across year (ordered by year)
            of a specific program tree version.

            Business rules: An acronym can be different across year
        """
        values = EducationGroupVersion.objects.filter(
            root_group__group_id=Subquery(
                GroupYear.objects.filter(
                    educationgroupversion__offer__acronym=program_tree_version_identity.offer_acronym,
                    educationgroupversion__version_name=program_tree_version_identity.version_name,
                    educationgroupversion__is_transition=program_tree_version_identity.is_transition,
                    academic_year__year=program_tree_version_identity.year,
                ).values('group_id')[:1]
            )
        ).annotate(
            offer_acronym=F('offer__acronym'),
            year=F('root_group__academic_year__year'),
        ).order_by('year').values('offer_acronym', 'year', 'version_name', 'is_transition')
        return [ProgramTreeVersionIdentity(**value) for value in values]


class NodeIdentitySearch(interface.DomainService):
    def get_from_program_tree_identity(self, tree_identity: 'ProgramTreeIdentity') -> 'NodeIdentity':
        return NodeIdentity(year=tree_identity.year, code=tree_identity.code)

    def get_from_training_identity(
            self,
            training_identity: 'TrainingIdentity',
            version_name: str = STANDARD,
            is_transition: str = False,
    ) -> 'NodeIdentity':
        values = GroupYear.objects.filter(
            educationgroupversion__offer__acronym=training_identity.acronym,
            educationgroupversion__offer__academic_year__year=training_identity.year,
            educationgroupversion__version_name=version_name,
            educationgroupversion__is_transition=is_transition,
        ).values(
            'partial_acronym'
        )
        if values:
            return NodeIdentity(code=values[0]['partial_acronym'], year=training_identity.year)

    def get_from_tree_version_identity(self, tree_version_id: 'ProgramTreeVersionIdentity') -> 'NodeIdentity':
        values = GroupYear.objects.filter(
            educationgroupversion__offer__acronym=tree_version_id.offer_acronym,
            educationgroupversion__offer__academic_year__year=tree_version_id.year,
            educationgroupversion__version_name=tree_version_id.version_name,
            educationgroupversion__is_transition=tree_version_id.is_transition,
        ).values(
            'partial_acronym',
        )
        if values:
            return NodeIdentity(code=values[0]['partial_acronym'], year=tree_version_id.year)

    @classmethod
    def get_from_element_id(cls, element_id: int) -> Union['NodeIdentity', None]:
        try:
            group_year = GroupYear.objects.values(
                'partial_acronym', 'academic_year__year'
            ).get(element__pk=element_id)
            return NodeIdentity(code=group_year['partial_acronym'], year=group_year['academic_year__year'])
        except GroupYear.DoesNotExist:
            return None

    def get_from_prerequisite_item(self, prerequisite_item: 'PrerequisiteItem') -> 'NodeIdentity':
        return NodeIdentity(code=prerequisite_item.code, year=prerequisite_item.year)


class ProgramTreeIdentitySearch(interface.DomainService):
    @classmethod
    def get_from_node_identity(cls, node_identity: 'NodeIdentity') -> 'ProgramTreeIdentity':
        return ProgramTreeIdentity(code=node_identity.code, year=node_identity.year)

    @classmethod
    def get_from_program_tree_version_identity(cls, identity: 'ProgramTreeVersionIdentity') -> 'ProgramTreeIdentity':
        return cls.get_from_node_identity(NodeIdentitySearch().get_from_tree_version_identity(identity))

    @classmethod
    def get_from_group_identity(cls, group_identity: 'GroupIdentity') -> 'ProgramTreeIdentity':
        return ProgramTreeIdentity(code=group_identity.code, year=group_identity.year)

    @classmethod
    def get_from_element_id(cls, element_id: 'int') -> 'ProgramTreeIdentity':
        node_identity = NodeIdentitySearch.get_from_element_id(element_id)
        return cls.get_from_node_identity(node_identity)


class TrainingIdentitySearch(interface.DomainService):

    @classmethod
    def get_from_program_tree_version_identity(
            cls,
            version_identity: 'ProgramTreeVersionIdentity'
    ) -> 'TrainingIdentity':
        return TrainingIdentity(acronym=version_identity.offer_acronym, year=version_identity.year)

    @classmethod
    def get_from_program_tree_identity(
            cls,
            identity: 'ProgramTreeIdentity'
    ) -> 'TrainingIdentity':
        return EducationGroupTrainingIdentitySearch().get_from_node_identity(
            node_identity=NodeIdentitySearch().get_from_program_tree_identity(tree_identity=identity)
        )


# TODO :: review : is this at the correct place?
class GroupIdentitySearch(interface.DomainService):
    def get_from_tree_version_identity(self, identity: 'ProgramTreeVersionIdentity') -> 'GroupIdentity':
        values = EducationGroupVersion.objects.filter(
            offer__acronym=identity.offer_acronym,
            offer__academic_year__year=identity.year,
            is_transition=identity.is_transition,
            version_name=identity.version_name,
        ).annotate(
            code=F('root_group__partial_acronym'),
            year=F('root_group__academic_year__year'),
        ).values('code', 'year')
        if values:
            return GroupIdentity(code=values[0]['code'], year=values[0]['year'])


class TrainingOrMiniTrainingOrGroupIdentitySearch(interface.DomainService):

    # FIXME :: This function calls another domain : we can't do that. It's the proof that we need to improve the
    # FIXME :: division of the roots Entities in the domain layer.
    @classmethod
    def get_from_program_tree_identity(
            cls,
            tree_identity: 'ProgramTreeIdentity'
    ) -> Union['GroupIdentity', 'MiniTrainingIdentity', 'TrainingIdentity']:
        data = _get_data_from_db(tree_identity)
        offer_acronym = data['offer_acronym']
        offer_type = data['offer_type']
        if not offer_acronym:
            return GroupIdentity(code=tree_identity.code, year=tree_identity.year)
        elif offer_type in MiniTrainingType.get_names():
            return MiniTrainingIdentity(acronym=offer_acronym, year=tree_identity.year)
        elif offer_type in TrainingType.get_names():
            return TrainingIdentity(acronym=offer_acronym, year=tree_identity.year)


def _get_data_from_db(tree_identity):
    return GroupYear.objects.annotate(
        offer_acronym=F('educationgroupversion__offer__acronym'),
        offer_type=F('educationgroupversion__offer__education_group_type__name'),
    ).values(
        'offer_acronym',
        'offer_type',
    ).get(
        partial_acronym=tree_identity.code,
        academic_year__year=tree_identity.year,
    )
