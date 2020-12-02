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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
import operator
import random
import string

import factory.fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from base.models.enums import attribution_procedure, learning_container_year_types
from base.models.enums import internship_subtypes
from base.models.enums import learning_unit_year_periodicity
from base.models.enums import learning_unit_year_session
from base.models.enums import learning_unit_year_subtypes
from base.models.enums import quadrimesters
from base.models.learning_unit_year import MINIMUM_CREDITS, MAXIMUM_CREDITS
from base.tests.factories import learning_component_year
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.campus import CampusFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from reference.tests.factories.language import LanguageFactory

fake = Faker()


def create_learning_units_year(start_year, end_year, learning_unit):
    return {year: LearningUnitYearFactory(academic_year=AcademicYearFactory(year=year), learning_unit=learning_unit)
            for year in range(start_year, end_year+1)}


def _is_internship(luy_obj):
    return luy_obj.learning_container_year \
           and luy_obj.learning_container_year.container_type == learning_container_year_types.INTERNSHIP


def _generate_internship_subtype(luy_obj):
    if _is_internship(luy_obj):
        return random.choice(internship_subtypes.INTERNSHIP_SUBTYPES)[0]
    return None


class LearningUnitYearFactory(DjangoModelFactory):
    class Meta:
        model = "base.LearningUnitYear"
        django_get_or_create = ('acronym', 'academic_year')

    external_id = factory.fuzzy.FuzzyText(length=10, chars=string.digits)
    academic_year = factory.SubFactory(AcademicYearFactory)
    learning_unit = factory.SubFactory("base.tests.factories.learning_unit.LearningUnitFactory")
    learning_container_year = factory.SubFactory(LearningContainerYearFactory,
                                                 academic_year=factory.SelfAttribute('..academic_year'))
    changed = factory.fuzzy.FuzzyNaiveDateTime(datetime.datetime(2016, 1, 1),
                                               datetime.datetime(2017, 3, 1))
    acronym = factory.Sequence(lambda n: 'LFAC1%03d' % n)
    specific_title = factory.Sequence(lambda n: 'Learning unit year - %d' % n)
    specific_title_english = factory.Sequence(lambda n: 'Learning unit year english - %d' % n)
    subtype = factory.Iterator(learning_unit_year_subtypes.LEARNING_UNIT_YEAR_SUBTYPES, getter=operator.itemgetter(0))

    internship_subtype = factory.LazyAttribute(_generate_internship_subtype)
    credits = factory.fuzzy.FuzzyDecimal(MINIMUM_CREDITS, MAXIMUM_CREDITS, precision=0)
    decimal_scores = False
    status = True
    session = factory.Iterator(learning_unit_year_session.LEARNING_UNIT_YEAR_SESSION, getter=operator.itemgetter(0))
    quadrimester = factory.Iterator(quadrimesters.LearningUnitYearQuadrimester.choices(),
                                    getter=operator.itemgetter(0))
    language = factory.SubFactory(LanguageFactory)
    attribution_procedure = None
    campus = factory.SubFactory(CampusFactory)
    periodicity = factory.Iterator(learning_unit_year_periodicity.PERIODICITY_TYPES, getter=operator.itemgetter(0))
    summary_locked = False

    @factory.post_generation
    def gen_acronym(self, create, extracted, **kwargs):
        if self.acronym:
            self.acronym = self.acronym.upper()


class LearningUnitYearWithComponentsFactory(LearningUnitYearFactory):
    lecturing_component = factory.PostGeneration(
        lambda obj, create, extracted, **kwargs: learning_component_year.LecturingLearningComponentYearFactory(
            learning_unit_year=obj,
            **kwargs
        )
    )
    practical_component = factory.PostGeneration(
        lambda obj, create, extracted, **kwargs: learning_component_year.PracticalLearningComponentYearFactory(
            learning_unit_year=obj,
            **kwargs
        )
    )


class LearningUnitYearFakerFactory(DjangoModelFactory):
    class Meta:
        model = "base.LearningUnitYear"

    external_id = factory.Sequence(lambda n: '10000000%02d' % n)
    academic_year = factory.LazyAttribute(lambda obj: obj.learning_container_year.academic_year)
    learning_unit = factory.SubFactory("base.tests.factories.learning_unit.LearningUnitFactory")
    learning_container_year = factory.SubFactory(
        LearningContainerYearFactory,
        academic_year=factory.SelfAttribute('..academic_year')
    )
    changed = fake.date_time_this_decade(before_now=True, after_now=True)
    acronym = factory.LazyAttribute(lambda obj: obj.learning_container_year.acronym)
    specific_title = factory.LazyAttribute(lambda obj: obj.learning_container_year.common_title)
    specific_title_english = None
    subtype = factory.Iterator(learning_unit_year_subtypes.LEARNING_UNIT_YEAR_SUBTYPES, getter=operator.itemgetter(0))
    internship_subtype = factory.Iterator(internship_subtypes.INTERNSHIP_SUBTYPES, getter=operator.itemgetter(0))
    credits = factory.fuzzy.FuzzyDecimal(MINIMUM_CREDITS, MAXIMUM_CREDITS, precision=0)
    decimal_scores = False
    status = True
    session = factory.Iterator(learning_unit_year_session.LEARNING_UNIT_YEAR_SESSION, getter=operator.itemgetter(0))
    quadrimester = factory.Iterator(quadrimesters.LearningUnitYearQuadrimester.choices(),
                                    getter=operator.itemgetter(0))
    language = factory.SubFactory(LanguageFactory)
    attribution_procedure = None
    campus = factory.SubFactory(CampusFactory)
    periodicity = factory.Iterator(learning_unit_year_periodicity.PERIODICITY_TYPES, getter=operator.itemgetter(0))


class LearningUnitYearFullFactory(LearningUnitYearFactory):
    subtype = learning_unit_year_subtypes.FULL


class LearningUnitYearPartimFactory(LearningUnitYearFactory):
    subtype = learning_unit_year_subtypes.PARTIM


def create_learning_unit_year(academic_yr, title, learning_unit):
    return LearningUnitYearFactory(acronym='LDROI1001',
                                   academic_year=academic_yr,
                                   subtype=learning_unit_year_subtypes.FULL,
                                   status=True,
                                   internship_subtype=None,
                                   credits=5,
                                   periodicity=learning_unit_year_periodicity.ANNUAL,
                                   language=None,
                                   professional_integration=True,
                                   specific_title=title,
                                   specific_title_english=None,
                                   quadrimester=quadrimesters.LearningUnitYearQuadrimester.Q1.name,
                                   session=learning_unit_year_session.SESSION_123,
                                   attribution_procedure=attribution_procedure.EXTERNAL,
                                   learning_unit=learning_unit
                                   )
