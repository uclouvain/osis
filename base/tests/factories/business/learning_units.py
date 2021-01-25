##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
import itertools
from decimal import Decimal

import factory.fuzzy

from base.models import academic_year as mdl_academic_year
from base.models.academic_year import LEARNING_UNIT_CREATION_SPAN_YEARS, compute_max_academic_year_adjournment
from base.models.enums import entity_type
from base.models.enums import learning_container_year_types, \
    learning_unit_year_periodicity, learning_unit_year_subtypes, component_type
from base.models.enums import learning_unit_year_session
from base.models.enums import organization_type
from base.models.enums import quadrimesters
from base.models.enums.component_type import DEFAULT_ACRONYM_COMPONENT
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.campus import CampusFactory
from base.tests.factories.entity import EntityWithVersionFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container import LearningContainerFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.teaching_material import TeachingMaterialFactory
from cms.tests.factories.translated_text import TranslatedTextFactory
from learning_unit.tests.factories.learning_class_year import LearningClassYearFactory
from reference.tests.factories.language import FrenchLanguageFactory


class LearningUnitsMixin:
    this_year = start_year = last_year = starting_academic_year = None
    old_academic_year = last_academic_year = oldest_academic_year = latest_academic_year = None
    learning_unit = learning_unit_year = learning_container_year = None
    list_of_academic_years = []
    list_of_academic_years_after_now = []
    list_of_odd_academic_years = []
    list_of_even_academic_years = []
    list_of_learning_units = []
    list_of_learning_container_year = []
    list_of_learning_unit_years = []

    @classmethod
    def setup_academic_years(cls):
        cls.this_year = datetime.datetime.now().year
        cls.start_year = AcademicYearFactory(year=cls.this_year - LEARNING_UNIT_CREATION_SPAN_YEARS * 2)
        cls.last_year = AcademicYearFactory(year=cls.this_year + LEARNING_UNIT_CREATION_SPAN_YEARS * 2)
        cls.list_of_academic_years = cls.create_list_of_academic_years(cls.start_year, cls.last_year)
        cls.starting_academic_year = mdl_academic_year.starting_academic_year()
        index_of_current_academic_year_in_list = cls.list_of_academic_years.index(cls.starting_academic_year)

        cls.oldest_academic_year = cls.list_of_academic_years[0]
        cls.latest_academic_year = cls.list_of_academic_years[-1]
        cls.old_academic_year = cls.list_of_academic_years[index_of_current_academic_year_in_list -
                                                           LEARNING_UNIT_CREATION_SPAN_YEARS]
        cls.last_academic_year = cls.list_of_academic_years[index_of_current_academic_year_in_list +
                                                            LEARNING_UNIT_CREATION_SPAN_YEARS]

        cls.list_of_academic_years_after_now = [
            academic_year for academic_year in cls.list_of_academic_years
            if (cls.starting_academic_year.year <= academic_year.year <= cls.last_academic_year.year)
        ]
        cls.list_of_odd_academic_years = [academic_year for academic_year in cls.list_of_academic_years_after_now
                                          if academic_year.year % 2]
        cls.list_of_even_academic_years = [academic_year for academic_year in cls.list_of_academic_years_after_now
                                           if not academic_year.year % 2]

    @staticmethod
    def create_list_of_academic_years(start_year, end_year):
        results = None
        if start_year and end_year:
            results = [AcademicYearFactory(year=year) for year in range(start_year.year, end_year.year + 1)]
        return results

    @staticmethod
    def setup_learning_unit(start_year, end_year=None):
        result = None
        if start_year:
            result = LearningUnitFactory(
                start_year=start_year,
                end_year=end_year)
        return result

    @staticmethod
    def setup_learning_container_year(academic_year, container_type):
        result = None
        if academic_year and container_type:
            result = LearningContainerYearFactory(
                academic_year=academic_year,
                container_type=container_type,
                requirement_entity=EntityWithVersionFactory(),
                allocation_entity=None
            )
        return result

    @staticmethod
    def setup_learning_unit_year(academic_year, learning_unit, learning_container_year, learning_unit_year_subtype,
                                 periodicity):
        create = False
        result = None
        end_year = learning_unit.end_year or AcademicYearFactory(year=compute_max_academic_year_adjournment())
        if learning_unit.start_year.year <= academic_year.year <= end_year.year:
            create = LearningUnitsMixin._has_to_be_created(academic_year, create, periodicity)

            if create:
                if not learning_container_year:
                    learning_container_year = LearningUnitsMixin.setup_learning_container_year(
                        academic_year, learning_container_year_types.COURSE
                    )

                result = LearningUnitYearFactory(
                    academic_year=academic_year,
                    learning_unit=learning_unit,
                    learning_container_year=learning_container_year,
                    subtype=learning_unit_year_subtype,
                    periodicity=periodicity
                )
        return result

    @staticmethod
    def _has_to_be_created(academic_year, create, periodicity):
        biennial_odd = periodicity == learning_unit_year_periodicity.BIENNIAL_ODD and not academic_year.year % 2
        biennial_even = periodicity == learning_unit_year_periodicity.BIENNIAL_EVEN and academic_year.year % 2
        annual = periodicity == learning_unit_year_periodicity.ANNUAL
        return any([biennial_odd, biennial_even, annual, create])

    @staticmethod
    def setup_list_of_learning_unit_years_full(list_of_academic_years, learning_unit_full, periodicity):
        results = []
        if not list_of_academic_years or not learning_unit_full:
            return results

        for academic_year in list_of_academic_years:

            new_luy = LearningUnitsMixin.setup_learning_unit_year(
                academic_year=academic_year,
                learning_unit=learning_unit_full,
                learning_container_year=None,
                learning_unit_year_subtype=learning_unit_year_subtypes.FULL,
                periodicity=periodicity)
            if new_luy:
                results.append(new_luy)

        return results

    @staticmethod
    def setup_list_of_learning_unit_years_partim(list_of_academic_years, learning_unit_full, learning_unit_partim):
        results = []
        if not list_of_academic_years or not learning_unit_full or not learning_unit_partim:
            return results

        for academic_year in list_of_academic_years:

            learning_unit_year_full = LearningUnitsMixin.setup_learning_unit_year(
                academic_year=academic_year,
                learning_unit=learning_unit_full,
                learning_container_year=None,
                learning_unit_year_subtype=learning_unit_year_subtypes.FULL,
                periodicity=learning_unit_year_periodicity.ANNUAL
            )

            if learning_unit_year_full:
                results.append(learning_unit_year_full)

                learning_unit_year_partim = LearningUnitsMixin.setup_learning_unit_year(
                    academic_year=academic_year,
                    learning_unit=learning_unit_partim,
                    learning_container_year=learning_unit_year_full.learning_container_year,
                    learning_unit_year_subtype=learning_unit_year_subtypes.PARTIM,
                    periodicity=learning_unit_year_periodicity.ANNUAL
                )
                if learning_unit_year_partim:
                    results.append(learning_unit_year_partim)

        return results

    @staticmethod
    def setup_educational_information(learning_unit_years_list):
        for luy in learning_unit_years_list:
            _create_fixed_educational_information_for_luy(luy)
        return learning_unit_years_list


class GenerateAcademicYear:
    def __init__(self, start_year, end_year):
        self.start_year = start_year
        self.end_year = end_year
        self.academic_years = LearningUnitsMixin.create_list_of_academic_years(start_year, end_year)

    def __getitem__(self, index):
        return self.academic_years[index]


def generate_academic_years(range=2):
    current_academic_year = create_current_academic_year()
    previous_years = GenerateAcademicYear(current_academic_year.year - range,
                                          current_academic_year.year - 1).academic_years
    next_years = GenerateAcademicYear(current_academic_year.year + 1, current_academic_year.year + range).academic_years
    return list(itertools.chain(previous_years, [current_academic_year], next_years))


class GenerateContainer:
    def __init__(self, start_year, end_year, parent_entity=None):
        self.parent_entity = parent_entity
        self.start_year = start_year
        self.end_year = end_year
        self.learning_container = LearningContainerFactory()
        self.learning_unit_full = LearningUnitFactory(learning_container=self.learning_container,
                                                      start_year=start_year,
                                                      end_year=end_year)
        self.learning_unit_partim = LearningUnitFactory(learning_container=self.learning_container,
                                                        start_year=start_year,
                                                        end_year=end_year
                                                        )

        self._setup_entities()
        self._setup_common_data()

        self.generated_container_years = [
            GenerateContainerYear(
                academic_year=AcademicYearFactory(year=year),
                learning_unit_full=self.learning_unit_full,
                learning_unit_partim=self.learning_unit_partim,
                entities=self.entities,
                campus=self.campus,
                language=self.language
            )
            for year in range(self.start_year.year, self.end_year.year + 1)
        ]

    def _setup_entities(self):
        self.entities = [
            EntityVersionFactory(
                start_date=datetime.datetime(1900, 1, 1),
                end_date=None,
                entity_type=entity_type.FACULTY,
                entity__organization__type=organization_type.MAIN,
                parent=self.parent_entity
            ).entity for _ in range(4)
        ]
        for entity in self.entities:
            entity.refresh_from_db()

    def _setup_common_data(self):
        self.language = FrenchLanguageFactory()
        self.campus = CampusFactory(name='Louvain-la-Neuve', organization__type=organization_type.MAIN)

    def __iter__(self):
        for generated_container_year in self.generated_container_years:
            yield generated_container_year

    def __getitem__(self, index):
        return self.generated_container_years[index]


class GenerateContainerYear:

    def __init__(self, academic_year, learning_unit_full, learning_unit_partim, entities, campus, language):
        self.academic_year = academic_year
        self.entities = entities
        self.campus = campus
        self.language = language

        self._setup_learning_container_year(learning_unit_full.learning_container)
        self._setup_learning_unit_year_full(learning_unit_full)
        self._setup_learning_unit_year_partim(learning_unit_partim)
        self._setup_learning_components_year()
        self.nb_classes = 5
        self._setup_classes()

    def _setup_learning_container_year(self, learning_container):
        self.requirement_entity_container_year = self.entities[0]
        self.allocation_entity_container_year = self.entities[1]
        self.additionnal_1_entity_container_year = self.entities[2]
        self.addtionnal_2_entity_container_year = self.entities[3]

        self.list_repartition_volume_entities = [
            self.requirement_entity_container_year,
            self.additionnal_1_entity_container_year,
            self.addtionnal_2_entity_container_year
        ]

        self.learning_container_year = LearningContainerYearFactory(
            learning_container=learning_container,
            academic_year=self.academic_year,
            container_type=learning_container_year_types.COURSE,
            acronym="LDROI1200",
            common_title="Droit international",
            common_title_english="Droit international english",
            requirement_entity=self.requirement_entity_container_year,
            allocation_entity=self.allocation_entity_container_year,
            additional_entity_1=self.additionnal_1_entity_container_year,
            additional_entity_2=self.addtionnal_2_entity_container_year,
        )
        self.learning_container = self.learning_container_year.learning_container

    def _setup_learning_unit_year_full(self, learning_unit):
        self.learning_unit_year_full = _setup_learning_unit_year(
            learning_unit, self.learning_container_year,
            learning_unit_year_subtypes.FULL,
            campus=self.campus,
            language=self.language
        )

    def _setup_learning_unit_year_partim(self, learning_unit):
        self.learning_unit_year_partim = _setup_learning_unit_year(
            learning_unit, self.learning_container_year,
            learning_unit_year_subtypes.PARTIM,
            campus=self.campus,
            language=self.language
        )

    def _setup_learning_components_year(self):
        self.learning_component_cm_full = _setup_learning_component_cm(
            self.learning_unit_year_full)
        self.learning_component_cm_partim = _setup_learning_component_cm(
            self.learning_unit_year_partim)
        self.learning_component_tp_full = _setup_learning_component_tp(
            self.learning_unit_year_full)
        self.learning_component_tp_partim = _setup_learning_component_tp(
            self.learning_unit_year_partim)

        self.list_components = [
            self.learning_component_cm_full,
            self.learning_component_tp_full,
            self.learning_component_cm_partim,
            self.learning_component_tp_partim
        ]

    def _setup_classes(self):
        for component in self.list_components:
            _setup_classes(component, number_classes=self.nb_classes)


def _setup_learning_unit_year(learning_unit, learning_container_year, subtype, campus, language):
    common_luy_data = _get_default_common_value_learning_unit_year(learning_container_year, subtype, language)
    learning_unit_year = LearningUnitYearFactory(
        learning_unit=learning_unit,
        learning_container_year=learning_container_year,
        academic_year=learning_container_year.academic_year,
        subtype=subtype,
        campus=campus,
        **common_luy_data
    )
    learning_unit = learning_unit_year.learning_unit
    learning_unit.learning_container = learning_container_year.learning_container
    learning_unit.save()
    return learning_unit_year


def _get_default_common_value_learning_unit_year(learning_container_year, subtype, language):
    """This function return all common data which must be equals in order to allow postponement"""
    common_data = {
        'acronym': learning_container_year.acronym,
        'specific_title': 'Title Specific',
        'specific_title_english': 'Title Specific English',
        'credits': Decimal(5),
        'session': learning_unit_year_session.SESSION_1X3,
        'quadrimester': quadrimesters.LearningUnitYearQuadrimester.Q1.name,
        'internship_subtype': None,
        'language': language,
        'periodicity': learning_unit_year_periodicity.ANNUAL,
        'other_remark': 'Other Remark',
        'other_remark_english': 'Other Remark in english',
        'faculty_remark': 'Faculty Remark'
    }
    if subtype == learning_unit_year_subtypes.PARTIM:
        common_data['acronym'] += 'A'
        common_data['specific_title'] += '(Partie I)'
        common_data['specific_title_english'] += '(Partim I)'
    return common_data


def _setup_learning_component_cm(learning_unit_year):
    return _setup_learning_component_year(learning_unit_year,
                                          component_type.LECTURING)


def _setup_learning_component_tp(learning_unit_year):
    return _setup_learning_component_year(learning_unit_year,
                                          component_type.PRACTICAL_EXERCISES)


def _setup_learning_component_year(learning_unit_year, component_type):
    return LearningComponentYearFactory(
        acronym=DEFAULT_ACRONYM_COMPONENT[component_type],
        learning_unit_year=learning_unit_year,
        type=component_type,
        planned_classes=1,
        hourly_volume_total_annual=30,
        hourly_volume_partial_q1=30,
        hourly_volume_partial_q2=0,
        repartition_volume_requirement_entity=30,
    )


def _setup_classes(learning_component_year, number_classes=5):
    for _ in range(number_classes):
        LearningClassYearFactory(learning_component_year=learning_component_year)


def _create_fixed_educational_information_for_luy(luy):
    _create_teaching_material_for_luy(luy)
    _create_cms_data_for_luy(luy)


def _create_teaching_material_for_luy(luy, quantity=10):
    for _ in range(quantity):
        TeachingMaterialFactory(learning_unit_year=luy)


def _create_cms_data_for_luy(luy, quantity=10):
    for _ in range(quantity):
        TranslatedTextFactory(reference=luy.id, text=factory.fuzzy.FuzzyText(length=255).fuzz())
