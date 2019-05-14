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

from base.tests.functionals.test_education_group import LoginPage
from features.steps.utils import SearchLearningUnitPage

use_step_matcher("re")


@given("La base de données est dans son état initial.")
def step_impl(context: Context):
    # TODO: Should be done in the real env.
    pass


@step("L'utilisateur est loggé en tant que gestionnaire facultaire ou central")
def step_impl(context: Context):
    page = LoginPage(driver=context.browser, base_url=context.get_url('/login/')).open()
    page.login('deryck', 'test')

    context.test.assertEqual(context.browser.current_url, context.get_url('/'))


@step("Aller sur la page (?P<url>.+)")
def step_impl(context: Context, url: str):
    # TODO find a solution to select the correct object page depending the given URL.
    context.current_page = SearchLearningUnitPage(driver=context.browser, base_url=context.get_url(url)).open()
    context.test.assertEqual(context.browser.current_url, context.get_url(url))


@step("Réinitialiser les critères de recherche")
def step_impl(context: Context):
    context.current_page.clear_button.click()


@when("Sélectionner (?P<anac>.+) dans la zone de saisie « Anac\. »")
def step_impl(context: Context, anac: str):
    context.current_page.anac = anac


@step("Encoder la valeur (?P<search_value>.+) dans la zone de saisie (?P<search_field>.+)")
def step_impl(context: Context, search_value: str, search_field: str):
    setattr(context.current_page, search_field, search_value)


@step("Cliquer sur le bouton Rechercher \(Loupe\)")
def step_impl(context: Context):
    context.current_page.search.click()


@then("Le nombre total de résultat est (?P<result_count>.+)")
def step_impl(context: Context, result_count: str):
    context.test.assertEqual(context.current_page.count_result(), result_count)


@step("Cocher la case « Avec ent. subord. »")
def step_impl(context: Context):
    raise NotImplementedError(u'STEP: And Cocher la case « Avec ent. subord. »')


@step("Dans la liste de résultat, le\(s\) premier\(s\) « Code » est\(sont\) bien (?P<acronym>.+)\.")
def step_impl(context: Context, acronym: str):
    raise NotImplementedError(
        u'STEP: And Dans la liste de résultat, le(s) premier(s) « Code » est(sont) bien <acronym>.')
