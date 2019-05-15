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

from features.steps.utils import SearchLearningUnitPage

use_step_matcher("re")


@step("Aller sur la page de recherche d'UE")
def step_impl(context: Context):
    url = '/learning_units/by_activity/'
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
    context.current_page.wait_for_page_to_load()


@then("Le nombre total de résultat est (?P<result_count>.+)")
def step_impl(context: Context, result_count: str):
    context.test.assertEqual(context.current_page.count_result(), result_count)


@step("Dans la liste de résultat, le\(s\) premier\(s\) « Code » est\(sont\) bien (?P<acronym>.+)\.")
def step_impl(context: Context, acronym: str):
    acronyms = acronym.split(',')
    for row, acronym in enumerate(acronyms):
        context.test.assertEqual(context.current_page.find_acronym_in_table(row + 1), acronym)


@when("Ouvrir le menu « Exporter »")
def step_impl(context: Context):
    context.current_page.export.click()


@step("Sélection « Liste personnalisée des unités d’enseignement »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.current_page.list_learning_units.click()


@step("Cocher les cases « Programmes/regroupements » et « Enseignant\(e\)s »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.current_page.with_program.click()
    context.current_page.with_tutor.click()


@step("Cliquer sur « Produire Excel »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.current_page.generate_xls.click()
