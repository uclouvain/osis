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
from behave import *
from behave.runner import Context

from base.tests.factories.user import SuperUserFactory
from base.tests.functionals.test_education_group import LoginPage

use_step_matcher("re")


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
