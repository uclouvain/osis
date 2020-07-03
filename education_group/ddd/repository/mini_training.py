# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from typing import Optional, List

from django.utils import timezone

from base.models.academic_year import AcademicYear as AcademicYearModelDb
from base.models.campus import Campus as CampusModelDb
from base.models.education_group_type import EducationGroupType as EducationGroupTypeModelDb
from base.models.entity_version import EntityVersion as EntityVersionModelDb
from education_group.ddd.domain import mini_training
from education_group.models.group import Group as GroupModelDb
from education_group.models.group_year import GroupYear as GroupYearModelDb
from osis_common.ddd import interface
from osis_common.ddd.interface import Entity, EntityIdentity


class MiniTrainingRepository(interface.AbstractRepository):
    @classmethod
    def create(cls, mini_training_obj: mini_training.MiniTraining) -> mini_training.MiniTrainingIdentity:
        start_year = AcademicYearModelDb.objects.get(year=mini_training_obj.year)
        end_year = AcademicYearModelDb.objects.get(year=mini_training_obj.end_year) if mini_training_obj.end_year else None
        education_group_type = EducationGroupTypeModelDb.objects.only('id').get(name=mini_training_obj.type.name)
        management_entity = EntityVersionModelDb.objects.current(timezone.now()).only('entity_id').get(
            acronym=mini_training_obj.management_entity.acronym,
        )
        teaching_campus = CampusModelDb.objects.only('id').get(
            name=mini_training_obj.teaching_campus.name,
            organization__name=mini_training_obj.teaching_campus.university_name
        )

        group_db_obj, _created = GroupModelDb.objects.update_or_create(
            pk=getattr(mini_training_obj.unannualized_identity, 'uuid', None),
            defaults={"start_year": start_year, "end_year": end_year}
        )
        mini_training_db_obj = GroupYearModelDb.objects.create(
            group=group_db_obj,
            academic_year=start_year,
            partial_acronym=mini_training_obj.code,
            education_group_type=education_group_type,
            acronym=mini_training_obj.abbreviated_title,
            title_fr=mini_training_obj.titles.title_fr,
            title_en=mini_training_obj.titles.title_en,
            credits=mini_training_obj.credits,
            constraint_type=mini_training_obj.content_constraint.type.name if mini_training_obj.content_constraint.type else None,
            min_constraint=mini_training_obj.content_constraint.minimum,
            max_constraint=mini_training_obj.content_constraint.maximum,
            management_entity_id=management_entity.entity_id,
            main_teaching_campus=teaching_campus,
        )

        return mini_training.MiniTrainingIdentity(
            code=mini_training_db_obj.partial_acronym,
            year=mini_training_db_obj.academic_year.year
        )

    @classmethod
    def update(cls, entity: Entity) -> EntityIdentity:
        pass

    @classmethod
    def get(cls, entity_id: EntityIdentity) -> Entity:
        pass

    @classmethod
    def search(cls, entity_ids: Optional[List[EntityIdentity]] = None, **kwargs) -> List[Entity]:
        pass

    @classmethod
    def delete(cls, entity_id: EntityIdentity) -> None:
        pass

