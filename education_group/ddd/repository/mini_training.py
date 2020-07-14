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

from django.db import IntegrityError
from django.db.models import Prefetch, Subquery, OuterRef
from django.utils import timezone

from base.models.academic_year import AcademicYear as AcademicYearModelDb
from base.models.campus import Campus as CampusModelDb
from base.models.education_group import EducationGroup as EducationGroupModelDb
from base.models.education_group_type import EducationGroupType as EducationGroupTypeModelDb
from base.models.education_group_year import EducationGroupYear as EducationGroupYearModelDb
from base.models.entity import Entity as EntityModelDb
from base.models.entity_version import EntityVersion as EntityVersionModelDb
from base.models.enums.active_status import ActiveStatusEnum
from base.models.enums.constraint_type import ConstraintTypeEnum
from base.models.enums.education_group_types import MiniTrainingType
from base.models.enums.schedule_type import ScheduleTypeEnum
from education_group.ddd.domain import mini_training, exception
from education_group.ddd.domain._campus import Campus
from education_group.ddd.domain._content_constraint import ContentConstraint
from education_group.ddd.domain._entity import Entity as EntityValueObject
from education_group.ddd.domain._remark import Remark
from education_group.ddd.domain._titles import Titles
from education_group.models.group import Group as GroupModelDb
from education_group.models.group_year import GroupYear as GroupYearModelDb
from osis_common.ddd import interface
from osis_common.ddd.interface import Entity, EntityIdentity
from program_management.models.education_group_version import EducationGroupVersion as EducationGroupVersionModelDb


class MiniTrainingRepository(interface.AbstractRepository):
    @classmethod
    def create(cls, mini_training_obj: mini_training.MiniTraining) -> mini_training.MiniTrainingIdentity:
        try:
            start_year = AcademicYearModelDb.objects.get(year=mini_training_obj.year)
            end_year = AcademicYearModelDb.objects.get(year=mini_training_obj.end_year) \
                if mini_training_obj.end_year else None
            education_group_type = EducationGroupTypeModelDb.objects.only('id').get(name=mini_training_obj.type.name)
            management_entity = EntityVersionModelDb.objects.current(timezone.now()).only('entity_id').get(
                acronym=mini_training_obj.management_entity.acronym,
            )
            teaching_campus = CampusModelDb.objects.only('id').get(
                name=mini_training_obj.teaching_campus.name,
                organization__name=mini_training_obj.teaching_campus.university_name
            )
        except AcademicYearModelDb.DoesNotExist:
            raise exception.AcademicYearNotFound
        except EducationGroupTypeModelDb.DoesNotExist:
            raise exception.TypeNotFound
        except EntityVersionModelDb.DoesNotExist:
            raise exception.ManagementEntityNotFound
        except CampusModelDb.DoesNotExist:
            raise exception.TeachingCampusNotFound

        group_db_obj, _created = GroupModelDb.objects.update_or_create(
            groupyear__partial_acronym=mini_training_obj.code,
            defaults={"start_year": start_year, "end_year": end_year}
        )

        try:
            mini_training_db_obj = GroupYearModelDb.objects.create(
                group=group_db_obj,
                academic_year=start_year,
                partial_acronym=mini_training_obj.code,
                education_group_type=education_group_type,
                acronym=mini_training_obj.abbreviated_title,
                title_fr=mini_training_obj.titles.title_fr,
                title_en=mini_training_obj.titles.title_en,
                credits=mini_training_obj.credits,
                constraint_type=mini_training_obj.content_constraint.type.name
                if mini_training_obj.content_constraint.type else None,
                min_constraint=mini_training_obj.content_constraint.minimum,
                max_constraint=mini_training_obj.content_constraint.maximum,
                management_entity_id=management_entity.entity_id,
                main_teaching_campus=teaching_campus,
            )

            education_group = EducationGroupModelDb.objects.create(
                start_year=start_year,
                end_year=end_year
            )

            offer = EducationGroupYearModelDb.objects.create(
                education_group=education_group,
                academic_year=start_year,
                partial_acronym=mini_training_obj.code,
                education_group_type=education_group_type,
                acronym=mini_training_obj.abbreviated_title,
                title=mini_training_obj.titles.title_fr,
                title_english=mini_training_obj.titles.title_en,
                credits=mini_training_obj.credits,
                constraint_type=mini_training_obj.content_constraint.type.name
                if mini_training_obj.content_constraint.type else None,
                min_constraint=mini_training_obj.content_constraint.minimum,
                max_constraint=mini_training_obj.content_constraint.maximum,
                management_entity_id=management_entity.entity_id,
                main_teaching_campus=teaching_campus,
                schedule_type=mini_training_obj.schedule_type.name,
                active=mini_training_obj.status.name
            )

            version = EducationGroupVersionModelDb.objects.create(
                root_group=mini_training_db_obj,
                offer=offer,
                is_transition=False,
                version_name="",
                title_en=mini_training_obj.titles.title_en,
                title_fr=mini_training_obj.titles.title_fr
            )
        except IntegrityError:
            raise exception.MiniTrainingCodeAlreadyExistException

        return mini_training.MiniTrainingIdentity(
            code=mini_training_db_obj.partial_acronym,
            year=mini_training_db_obj.academic_year.year
        )

    @classmethod
    def update(cls, entity: Entity) -> EntityIdentity:
        pass

    @classmethod
    def get(cls, entity_id: mini_training.MiniTrainingIdentity) -> mini_training.MiniTraining:
        try:
            version = EducationGroupVersionModelDb.objects.filter(
                root_group__partial_acronym=entity_id.code,
                root_group__academic_year__year=entity_id.year
            ).select_related(
                "offer",
                "root_group",
                "root_group__academic_year",
                "root_group__group__start_year",
                "root_group__group__end_year",
                "root_group__education_group_type",
                "root_group__main_teaching_campus__organization"
            ).prefetch_related(
                Prefetch(
                    'root_group__management_entity',
                    EntityModelDb.objects.all().annotate(
                        most_recent_acronym=Subquery(
                            EntityVersionModelDb.objects.filter(
                                entity__id=OuterRef('pk')
                            ).order_by('-start_date').values('acronym')[:1]
                        )
                    )
                ),
            ).get()
        except EducationGroupVersionModelDb.DoesNotExist:
            raise exception.MiniTrainingNotFoundException
        return mini_training.MiniTraining(entity_identity=entity_id,
                                          type=_convert_type(version.root_group.education_group_type),
                                          abbreviated_title=version.root_group.acronym, titles=Titles(
                title_fr=version.root_group.title_fr,
                title_en=version.root_group.title_en,
            ), status=ActiveStatusEnum[version.offer.active] if version.offer.active else None,
                                          schedule_type=ScheduleTypeEnum[
                                              version.offer.schedule_type] if version.offer.schedule_type else None,
                                          credits=version.root_group.credits, content_constraint=ContentConstraint(
                type=ConstraintTypeEnum[version.root_group.constraint_type]
                if version.root_group.constraint_type else None,
                minimum=version.root_group.min_constraint,
                maximum=version.root_group.max_constraint,
            ), management_entity=EntityValueObject(
                acronym=version.root_group.management_entity.most_recent_acronym,
            ), teaching_campus=Campus(
                name=version.root_group.main_teaching_campus.name,
                university_name=version.root_group.main_teaching_campus.organization.name,
            ), remark=Remark(
                text_fr=version.root_group.remark_fr,
                text_en=version.root_group.remark_en
            ), start_year=version.root_group.group.start_year.year,
                                          end_year=version.root_group.group.end_year.year if version.root_group.group.end_year else None)

    @classmethod
    def search(cls, entity_ids: Optional[List[EntityIdentity]] = None, **kwargs) -> List[Entity]:
        pass

    @classmethod
    def delete(cls, entity_id: EntityIdentity) -> None:
        pass


def _convert_type(education_group_type):
    if education_group_type.name in MiniTrainingType.get_names():
        return MiniTrainingType[education_group_type.name]
    raise Exception('Unsupported group type')
