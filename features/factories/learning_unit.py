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
import random

import factory

from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.business.learning_units import edition
from base.models.academic_year import AcademicYear, current_academic_year
from base.models.campus import Campus
from base.models.entity_version import EntityVersion
from base.models.enums import learning_container_year_types
from base.models.enums.entity_type import PEDAGOGICAL_ENTITY_TYPES, FACULTY
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.learning_component_year import LecturingLearningComponentYearFactory, \
    PracticalLearningComponentYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFullFactory
from base.tests.factories.tutor import TutorFactory
from features.factories.reference import BusinessLanguageFactory


class LearningUnitBusinessFactory:
    def __init__(self):
        BusinessLanguageFactory()
        BusinessLearningFactory()
        BusinessAttributionFactory()


class BusinessAttributionFactory:
    def __init__(self):
        self.tutors = TutorFactory.create_batch(60)
        luys_to_attribute = LearningUnitYear.objects.filter(
            academic_year=current_academic_year()
        ).prefetch_related(
            "learningcomponentyear_set"
        )
        for luy in luys_to_attribute:
            self._attribute_tutors_to_learning_unit_year(luy)

    def _attribute_tutors_to_learning_unit_year(self, luy: LearningUnitYear):
        number_tutors_to_attribute = random.randint(0, 3)
        tutors_to_attribute = random.sample(self.tutors, number_tutors_to_attribute)

        components = list(luy.learningcomponentyear_set.all())
        for tutor in tutors_to_attribute:
            AttributionChargeNewFactory.create_batch(
                len(components),
                attribution__tutor=tutor,
                learning_component_year=factory.Iterator(components)
            )


class BusinessLearningFactory:
    def __init__(self):
        self.learning_units = BusinessLearningUnitFactory.create_batch(
            20,
            start_year__year=2015
        )
        self._assign_learning_unit_to_faculty()

    def _assign_learning_unit_to_faculty(self):
        faculties = EntityVersion.objects.filter(entity_type=FACULTY).select_related("entity")
        self.learning_units += BusinessLearningUnitFactory.create_batch(
            len(faculties),
            start_year__year=2015,
            learningunityears__learning_container_year__requirement_entity=factory.Iterator(faculties, getter=lambda ev: ev.entity)
        )


class BusinessLearningUnitFactory(LearningUnitFactory):
    @factory.post_generation
    def learningunityears(obj, create, extracted, **kwargs):
        starting_learning_unit_year = BusinessLearningUnitYearFactory(
            academic_year=obj.start_year,
            **kwargs
        )
        academic_years = AcademicYear.objects.filter(
            year__gt=obj.start_year.year,
        )
        if obj.end_year:
            academic_years = academic_years.filter(year__lte=obj.end_year.year)

        for acy in academic_years:
            edition.duplicate_learning_unit_year(starting_learning_unit_year, acy)


class BusinessLearningUnitContainerYearFactory(LearningContainerYearFactory):
    requirement_entity = factory.LazyFunction(
        lambda: EntityVersion.objects.filter(entity_type__in=PEDAGOGICAL_ENTITY_TYPES).order_by("?").first().entity
    )
    allocation_entity = factory.LazyAttribute(lambda o: o.requirement_entity)
    container_type = learning_container_year_types.COURSE


class BusinessLearningUnitYearFactory(LearningUnitYearFullFactory):
    campus = factory.LazyFunction(lambda: Campus.objects.all().order_by("?").first())
    internship_subtype = None
    learning_container_year = factory.SubFactory(
        BusinessLearningUnitContainerYearFactory,
        academic_year=factory.SelfAttribute('..academic_year')
    )

    @factory.post_generation
    def create_components(obj, create, extracted, **kwargs):
        LecturingLearningComponentYearFactory(learning_unit_year=obj)
        PracticalLearningComponentYearFactory(learning_unit_year=obj)


