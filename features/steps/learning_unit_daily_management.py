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
from django.urls import reverse

from base.models.learning_unit_year import LearningUnitYear
from features.steps.utils import LearningUnitPage, LoginPage

use_step_matcher("re")


@step("La période de modification des programmes est en cours")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    #FIXME
    page = LoginPage(driver=context.browser, base_url=context.get_url('/login/')).open()
    page.login('deryck', 'test')

    context.test.assertEqual(context.browser.current_url, context.get_url('/'))

@step("L’utilisateur est dans le groupe « faculty manager »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass
    # raise NotImplementedError(u'STEP: And L’utilisateur est dans le groupe « faculty manager »')


@step("L’utilisateur est attaché à l’entité DRT")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass
    # raise NotImplementedError(u'STEP: And L’utilisateur est attaché à l’entité DRT')


@when("Cliquer sur le menu « Actions »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.current_page.actions.click()


@then("L’action « Modifier » est désactivée.")
def step_impl(context: Context):
    context.test.assertTrue(context.current_page.is_li_edit_link_disabled())


@given("Aller sur la page de detail de l'ue: (?P<acronym>.+)")
def step_impl(context: Context, acronym: str):
    luy = LearningUnitYear.objects.get(acronym=acronym, academic_year__year=2019)
    url = reverse('learning_unit', args=[luy.pk])

    context.current_page = LearningUnitPage(driver=context.browser, base_url=context.get_url(url)).open()
    context.test.assertEqual(context.browser.current_url, context.get_url(url))


@then("L’action « Modifier » est activée.")
def step_impl(context: Context):
    context.test.assertFalse(context.current_page.is_li_edit_link_disabled())
