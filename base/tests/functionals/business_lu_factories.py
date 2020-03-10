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
from django.conf import settings

from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.business.learning_units import edition
from base.models.academic_year import AcademicYear, current_academic_year
from base.models.campus import Campus
from base.models.entity import Entity
from base.models.entity_version import EntityVersion
from base.models.enums import entity_type, learning_container_year_types
from base.models.enums.entity_type import PEDAGOGICAL_ENTITY_TYPES, FACULTY
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.campus import CampusFactory
from base.tests.factories.entity_version import MainEntityVersionFactory
from base.tests.factories.learning_component_year import LecturingLearningComponentYearFactory, \
    PracticalLearningComponentYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFullFactory
from base.tests.factories.organization import MainOrganizationFactory
from base.tests.factories.person import FacultyManagerFactory, CentralManagerFactory
from base.tests.factories.person_entity import PersonEntityFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import SuperUserFactory
from reference.tests.factories.language import LanguageFactory
from testing.providers import LANGUAGES


class LearningUnitBusinessFactory:
    def __init__(self):
        SuperUserFactory()
        BusinessAcademicYearFactory()
        BusinessLanguageFactory()
        BusinessEntityVersionTreeFactory()
        BusinessCampusFactory()
        BusinessLearningFactory()
        BusinessAttributionFactory()

        self.central_manager = BusinessCentralManagerFactory()
        self.faculty_manager = BusinessFacultyManagerFactory()


class BusinessFacultyManagerFactory(FacultyManagerFactory):
    def __init__(self, *args, **kwargs):
        permissions = (
            'can_access_learningunit',
            'can_edit_learningunit_date',
            'can_edit_learningunit',
            'can_create_learningunit',
            'can_edit_learning_unit_proposal',
            'can_propose_learningunit',
            'can_consolidate_learningunit_proposal',
            'can_access_education_group',
            'add_educationgroup',
        )
        factory_parameters = {
            "user__username": "faculty_manager",
            "user__first_name": "Faculty",
            "user__last_name": "Manager",
            "user__password": "Faculty_Manager",
            "language": settings.LANGUAGE_CODE_FR
        }

        super().__init__(*permissions, *args, **factory_parameters, **kwargs)
        entity = Entity.objects.filter(entityversion__entity_type=entity_type.SECTOR).order_by("?").first()
        PersonEntityFactory(
            person=self.person,
            entity=entity,
            with_child=True
        )


class BusinessCentralManagerFactory(CentralManagerFactory):
    def __init__(self, *args, **kwargs):
        permissions = (
            'can_access_learningunit',
            'can_edit_learningunit_date',
            'can_edit_learningunit',
            'can_create_learningunit',
            'can_edit_learning_unit_proposal',
            'can_propose_learningunit',
            'can_consolidate_learningunit_proposal',
            'can_access_education_group',
            'add_educationgroup'
        )
        factory_parameters = {
            "user__username": "central_manager",
            "user__first_name": "Central",
            "user__last_name": "Manager",
            "user__password": "Central_Manager",
            "language": settings.LANGUAGE_CODE_FR
        }

        super().__init__(*permissions, *args, **factory_parameters, **kwargs)
        entity = Entity.objects.filter(entityversion__entity_type="").order_by("?").first()
        PersonEntityFactory(
            person=self.person,
            entity=entity,
            with_child=True
        )


class BusinessAcademicYearFactory:
    def __init__(self):
        self.academic_years = AcademicYearFactory.produce(number_past=10, number_future=10)


class BusinessLanguageFactory:
    def __init__(self):
        self.languages = LanguageFactory.create_batch(
            len(LANGUAGES),
            _language=factory.Iterator(LANGUAGES)
        )


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


class BusinessCampusFactory:
    def __init__(self):
        main_organization = MainOrganizationFactory()
        self.main_campus = CampusFactory.create_batch(5, organization=main_organization)


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


class BusinessEntityVersionTreeFactory:

    class Node:
        def __init__(self, element: EntityVersion):
            self.element = element
            self.children = []

    def __init__(self):
        self.root = self.Node(MainEntityVersionFactory(parent=None, entity_type=""))
        self.nodes = [self.root]
        self._genererate_tree(self.root)

    def _genererate_tree(self, parent: Node):
        number_nodes_to_generate = random.randint(1, 6)
        for _ in range(number_nodes_to_generate):
            child_entity_type = self.entity_type_to_generate(parent.element.entity_type)
            if child_entity_type is None:
                continue

            child = self.Node(
                MainEntityVersionFactory(parent=parent.element.entity, entity_type=child_entity_type)
            )
            parent.children.append(child)
            self.nodes.append(child)

            self._genererate_tree(child)

    def entity_type_to_generate(self, parent_entity_type):
        type_based_on_parent_type = {
            entity_type.SECTOR: (entity_type.FACULTY, entity_type.LOGISTICS_ENTITY),
            entity_type.FACULTY: (entity_type.PLATFORM, entity_type.SCHOOL, entity_type.INSTITUTE),
            entity_type.LOGISTICS_ENTITY: (entity_type.INSTITUTE, ),
            entity_type.SCHOOL: (None, ),
            entity_type.INSTITUTE: (None, entity_type.POLE, entity_type.PLATFORM),
            entity_type.POLE: (None, ),
            entity_type.DOCTORAL_COMMISSION: (None, ),
            entity_type.PLATFORM: (None, ),
        }
        return random.choice(
            type_based_on_parent_type.get(parent_entity_type, (entity_type.SECTOR, ))
        )
