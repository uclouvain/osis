############################################################################
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
############################################################################
import factory

from base.business.education_groups import postponement
from base.models.academic_year import AcademicYear
from base.models.campus import Campus
from base.models.entity_version import EntityVersion
from base.models.enums import education_group_types
from base.models.enums.entity_type import PEDAGOGICAL_ENTITY_TYPES
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_type import TrainingEducationGroupTypeFactory, \
    MiniTrainingEducationGroupTypeFactory, GroupEducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory


class OfferBusinessFactory:
    def __init__(self):
        BusinessEducationGroupTypeFactory()
        BusinessOfferFactory()


class BusinessEducationGroupTypeFactory:
    def __init__(self):
        self.trainings = TrainingEducationGroupTypeFactory.create_batch(
            len(list(education_group_types.TrainingType))
        )
        self.minitrainings = MiniTrainingEducationGroupTypeFactory.create_batch(
            len(list(education_group_types.MiniTrainingType))
        )
        self.groups = GroupEducationGroupTypeFactory.create_batch(
            len(list(education_group_types.GroupType))
        )


class BusinessOfferFactory:
    def __init__(self):
        self.offers = BusinessEducationGroupFactory.create_batch(
            20,
            start_year__year=2015
        )


class BusinessEducationGroupFactory(EducationGroupFactory):
    @factory.post_generation
    def educationgroupyears(obj, create, extracted, **kwargs):
        starting_education_group_year = BusinessEducationGroupYearFactory(
            education_group=obj,
            academic_year=obj.start_year,
            **kwargs
        )
        academic_years = AcademicYear.objects.filter(year__gt=obj.start_year.year)
        if obj.end_year:
            academic_years = academic_years.filter(year__lte=obj.end_year.year)

        for acy in academic_years:
            postponement.duplicate_education_group_year(
                starting_education_group_year,
                acy
            )


class BusinessEducationGroupYearFactory(EducationGroupYearFactory):
    management_entity = factory.LazyFunction(
        lambda: EntityVersion.objects.filter(entity_type__in=PEDAGOGICAL_ENTITY_TYPES).order_by("?").first().entity
    )
    administration_entity = factory.LazyAttribute(lambda o: o.management_entity)
    enrollment_campus = factory.LazyFunction(lambda: Campus.objects.all().order_by("?").first())
