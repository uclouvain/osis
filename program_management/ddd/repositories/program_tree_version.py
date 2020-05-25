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
from typing import Optional, List

from django.db.models import Q, F

from education_group.models.group_year import GroupYear
from osis_common.ddd import interface
from osis_common.ddd.interface import EntityIdentity
from program_management.ddd.business_types import *
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.ddd.domain.program_tree_version import ProgramTreeVersion
from program_management.ddd.domain.program_tree import ProgramTreeIdentity
from program_management.ddd.repositories import load_tree
from program_management.ddd.repositories.program_tree import ProgramTreeRepository
from program_management.models.education_group_version import EducationGroupVersion
from program_management.models.element import Element


class ProgramTreeVersionRepository(interface.AbstractRepository):

    # @classmethod
    # def get(cls, entity_id: 'ProgramTreeVersionIdentity') -> 'ProgramTreeVersion':
    #     search_result = cls.search(entity_ids=[entity_id])
    #     if search_result:
    #         return search_result[0]

    # @classmethod
    # def search(cls, entity_ids: Optional[List[EntityIdentity]] = None, **kwargs) -> List['ProgramTreeVersion']:
    #     if entity_ids:
    #         return _search_by_entity_ids(entity_ids)
    #     return []

    @classmethod
    def search_all_versions_from_root_node(cls, root_node_identity: 'NodeIdentity') -> List['ProgramTreeVersion']:
        qs = GroupYear.objects.filter(
            partial_acronym=root_node_identity.code,
            academic_year__year=root_node_identity.year,
        ).order_by(
            'educationgroupversion__version_name'
        ).annotate(
            offer_acronym=F('educationgroupversion__offer__acronym'),
            offer_year=F('educationgroupversion__offer__academic_year__year'),
            version_name=F('educationgroupversion__version_name'),
            version_title_fr=F('educationgroupversion__title_fr'),
            version_title_en=F('educationgroupversion__title_en'),
            is_transition=F('educationgroupversion__is_transition'),
        ).values(
            'offer_acronym',
            'offer_year',
            'version_name',
            'version_title_fr',
            'version_title_en',
            'is_transition',
        )
        results = []
        for record_dict in qs:
            results.append(
                ProgramTreeVersion(
                    entity_identity=ProgramTreeVersionIdentity(
                        record_dict['offer_acronym'],
                        record_dict['offer_year'],
                        record_dict['version_name'],
                        record_dict['is_transition'],
                    ),
                    program_tree_identity=ProgramTreeIdentity(root_node_identity.code, root_node_identity.year),
                    program_tree_repository=ProgramTreeRepository,
                    title_fr=record_dict['version_title_fr'],
                    title_en=record_dict['version_title_en'],
                )
            )
        return results


# def _search_by_entity_ids(entity_ids) -> List['ProgramTreeVersion']:
#     qs = Element.objects.all()
#     filter_search_from = _build_where_clause(entity_ids[0])
#     for identity in entity_ids[1:]:
#         filter_search_from |= _build_where_clause(identity)
#     qs = qs.filter(filter_search_from)
#     # FIXME :: implement load_version into this function ProgramTreeVersionRepository.get()
#     return load_tree.load_version(qs.values_list('pk', flat=True))
#
#
# def _build_where_clause(program_version_identity: 'ProgramTreeVersionIdentity') -> Q:
#     return Q(
#         group_year__education_group_version__version_name=program_version_identity.version_name,
#         group_year__education_group_version__education_group_year_id=program_version_identity.offer_id,
#         group_year__education_group_version__is_transition=program_version_identity.is_transition,
#     )
