# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from datetime import timedelta, datetime

from behave import *
from behave.runner import Context

from base.models.academic_calendar import AcademicCalendar
from base.models.academic_year import AcademicYear, current_academic_year
from base.models.entity import Entity
from base.models.enums.academic_calendar_type import EDUCATION_GROUP_EDITION
from base.models.person_entity import PersonEntity
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import FacultyManagerFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from base.tests.factories.user import SuperUserFactory
from base.tests.functionals.test_education_group import LoginPage

use_step_matcher("parse")


@given("La base de données est dans son état initial.")
def step_impl(context: Context):
    # TODO: Should be done in the real env.
    pass


@step("L'utilisateur est loggé en tant que gestionnaire facultaire ou central")
def step_impl(context: Context):
    context.user = SuperUserFactory(username="usual_suspect", first_name="Keyser", last_name="Söze",
                                    password="Roger_Verbal_Kint")

    page = LoginPage(driver=context.browser, base_url=context.get_url('/login/')).open()
    page.login("usual_suspect", 'Roger_Verbal_Kint')

    context.test.assertEqual(context.browser.current_url, context.get_url('/'))


@step("{acronym} est en proposition en {year} lié à {entity}")
def step_impl(context, acronym, year, entity):
    ac = AcademicYear.objects.get(year=year[:4])
    luy = LearningUnitYearFactory(acronym=acronym, academic_year=ac)
    entity = Entity.objects.filter(entityversion__acronym=entity).last()
    ProposalLearningUnitFactory(learning_unit_year=luy,
                                entity=entity,
                                folder_id=12)


@step("La période de modification des programmes est en cours")
def step_impl(context: Context):
    calendar = AcademicCalendar.objects.get(academic_year=current_academic_year(), reference=EDUCATION_GROUP_EDITION)
    calendar.end_date = (datetime.now() + timedelta(days=1)).date()
    calendar.save()


@step("L’utilisateur est dans le groupe « faculty manager »")
def step_impl(context: Context):
    person = FacultyManagerFactory(
        user__username="usual_suspect",
        user__first_name="Keyser",
        user__last_name="Söze",
        user__password="Roger_Verbal_Kint",
    )

    person.user.superuser = True
    person.user.save()
    context.user = person.user

    page = LoginPage(driver=context.browser, base_url=context.get_url('/login/')).open()
    page.login("usual_suspect", 'Roger_Verbal_Kint')

    context.test.assertEqual(context.browser.current_url, context.get_url('/'))


@step("L’utilisateur est attaché à l’entité {value}")
def step_impl(context: Context, value: str):
    entity = Entity.objects.filter(entityversion__acronym=value).first()
    PersonEntity.objects.get_or_create(person=context.user.person, entity=entity, defaults={'with_child': True})
