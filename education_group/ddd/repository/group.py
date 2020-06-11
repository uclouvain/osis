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

from django.db.models import Prefetch, Subquery, OuterRef

from base.models.entity import Entity
from base.models.entity_version import EntityVersion
from base.models.enums.constraint_type import ConstraintTypeEnum
from base.models.enums.education_group_types import GroupType
from education_group.ddd.domain import exception, group
from education_group.ddd.domain._campus import Campus
from education_group.ddd.domain._content_constraint import ContentConstraint
from education_group.ddd.domain._remark import Remark
from education_group.ddd.domain._titles import Titles
from education_group.ddd.domain._entity import Entity as EntityValueObject
from education_group.models.group_year import GroupYear
from education_group.ddd.business_types import *
from osis_common.ddd import interface


class GroupRepository(interface.AbstractRepository):
    @classmethod
    def create(cls, entity: 'Group') -> 'GroupIdentity':
        raise NotImplementedError

    @classmethod
    def update(cls, entity: 'Group') -> 'GroupIdentity':
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: 'GroupIdentity') -> 'Group':
        qs = GroupYear.objects.filter(
            partial_acronym=entity_id.code,
            academic_year__year=entity_id.year
        ).select_related(
            'academic_year',
            'education_group_type',
            'main_teaching_campus__organization',
            'group__start_year',
            'group__end_year',
        ).prefetch_related(
            Prefetch(
                'management_entity',
                Entity.objects.all().annotate(
                    most_recent_acronym=Subquery(
                        EntityVersion.objects.filter(
                            entity__id=OuterRef('pk')
                        ).order_by('-start_date').values('acronym')[:1]
                    )
                )
            ),
        )
        try:
            obj = qs.get()
        except GroupYear.DoesNotExist:
            raise exception.GroupNotFoundException

        return group.Group(
            entity_identity=entity_id,
            type=GroupType[obj.education_group_type.name],
            abbreviated_title=obj.acronym,
            titles=Titles(
                title_fr=obj.title_fr,
                title_en=obj.title_en,
            ),
            credits=obj.credits,
            content_constraint=ContentConstraint(
                type=ConstraintTypeEnum[obj.constraint_type],
                minimum=obj.min_constraint,
                maximum=obj.max_constraint,
            ),
            management_entity=EntityValueObject(
                acronym=obj.management_entity.most_recent_acronym,
            ),
            teaching_campus=Campus(
                name=obj.main_teaching_campus.name,
                university_name=obj.main_teaching_campus.organization.name,
            ),
            remark=Remark(
                text_fr=obj.remark_fr,
                text_en=obj.remark_en
            ),
            start_year=obj.group.start_year.year,
            end_year=obj.group.end_year.year if obj.group.end_year else None,
        )

    @classmethod
    def search(cls, entity_ids: Optional[List['GroupIdentity']] = None, **kwargs) -> List['Group']:
        raise NotImplementedError

    @classmethod
    def delete(cls, entity_id: 'GroupIdentity') -> None:
        raise NotImplementedError
