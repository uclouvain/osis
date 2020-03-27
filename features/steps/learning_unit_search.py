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
import os
import random

from behave import *
from behave.runner import Context
from django.utils.translation import gettext_lazy as _

from base.models import tutor
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.learning_unit_year import LearningUnitYear
from base.models.tutor import Tutor
from features.forms.learning_units import search_form
from features.pages.learning_unit.pages import SearchLearningUnitPage

use_step_matcher("re")


@step("Aller sur la page de recherche d'UE")
def step_impl(context: Context):
    url = '/learning_units/by_activity/'
    SearchLearningUnitPage(driver=context.browser, base_url=context.get_url(url)).open()
    context.test.assertEqual(context.browser.current_url, context.get_url(url))


@step("Réinitialiser les critères de recherche")
def step_impl(context: Context):
    page = SearchLearningUnitPage(driver=context.browser)
    page.clear_button.click()


@step("Cliquer sur le bouton Rechercher \(Loupe\)")
def step_impl(context: Context):
    page = SearchLearningUnitPage(driver=context.browser)
    page.search.click()
    page.wait_for_page_to_load()  # FIXME remove the implicit wait should be on the click


@then("Le nombre total de résultat est (?P<result_count>.+)")
def step_impl(context: Context, result_count: str):
    page = SearchLearningUnitPage(driver=context.browser)
    context.test.assertEqual(page.count_result(), result_count)


@step("Dans la liste de résultat, le\(s\) premier\(s\) « Code » est\(sont\) bien (?P<acronym>.+)\.")
def step_impl(context: Context, acronym: str):
    page = SearchLearningUnitPage(driver=context.browser)
    acronyms = acronym.split(',')
    acronyms_results = [result.acronym.text for result in page.proposal_results]
    for row, acronym in enumerate(acronyms):
        context.test.assertTrue(acronym in acronyms_results)


@when("Ouvrir le menu « Exporter »")
def step_impl(context: Context):
    page = SearchLearningUnitPage(driver=context.browser)
    page.export.click()


@step("Sélection « Liste personnalisée des unités d’enseignement »")
def step_impl(context: Context):
    page = SearchLearningUnitPage(driver=context.browser)
    page.list_learning_units.click()


@step("Cocher les cases « Programmes/regroupements » et « Enseignant\(e\)s »")
def step_impl(context: Context):
    page = SearchLearningUnitPage(driver=context.browser)
    page.with_program.click()
    page.with_tutor.click()


@step("Cliquer sur « Produire Excel »")
def step_impl(context: Context):
    page = SearchLearningUnitPage(driver=context.browser)
    page.generate_xls.click()


@step("Sélectionner l’onglet « Propositions »")
def step_impl(context: Context):
    page = SearchLearningUnitPage(driver=context.browser)
    page.proposal_search.click()


@step("Encoder le code d'une UE")
def step_impl(context: Context):
    page = SearchLearningUnitPage(driver=context.browser)
    form_values = search_form.fill_code(page)
    context.search_form_values = form_values


@step("Encoder le type d'UE")
def step_impl(context: Context):
    page = SearchLearningUnitPage(driver=context.browser)
    context.type_to_search = random.choice(LearningContainerYearType.get_values())
    page.container_type = context.type_to_search


@step("Encoder l'entité d'UE")
def step_impl(context: Context):
    page = SearchLearningUnitPage(driver=context.browser)
    context.search_form_values = search_form.fill_entity(page)


@step("Encoder l'enseignant d'UE")
def step_impl(context: Context):
    page = SearchLearningUnitPage(driver=context.browser)
    context.search_form_values = search_form.fill_tutor(page)


@step("La liste de résultat doit correspondre aux crières de recherche")
def step_impl(context: Context):
    page = SearchLearningUnitPage(driver=context.browser)
    search_criterias = context.search_form_values
    assert_acronym_match(page.results, search_criterias.get("acronym", ""), context.test)
    assert_requirement_entity_match(page.results, search_criterias.get("requirement_entity", ""), context.test)
    assert_tutor_match(page.results, search_criterias.get("tutor", ""), context.test)


@step("Dans la liste de résultat, seul ce type doit apparaître")
def step_impl(context: Context):
    page = SearchLearningUnitPage(driver=context.browser)
    learning_unit_types_present_in_page = set([result.type.text for result in page.results])
    context.test.assertEqual(
        {context.type_to_search},
        learning_unit_types_present_in_page
    )


@then("Le fichier excel devrait être présent")
def step_impl(context: Context):
    filename = "{}.xlsx".format(_('LearningUnitsList'))
    full_path = os.path.join(context.download_directory, filename)
    context.test.assertTrue(os.path.exists(full_path), full_path)


@step("suspend")
def step_impl(context: Context):
    import time
    time.sleep(10)


def assert_acronym_match(results: SearchLearningUnitPage.LearningUnitElement, acronym: str, assertions):
    if not acronym:
        return
    for result in results:
        assertions.assertIn(acronym, result.acronym.text)


def assert_requirement_entity_match(
        results: SearchLearningUnitPage.LearningUnitElement,
        requirement_entity: str,
        assertions
):
    if not requirement_entity:
        return
    for result in results:
        assertions.assertEqual(result, result.requirement_entity.text)


def assert_tutor_match(
        results: SearchLearningUnitPage.LearningUnitElement,
        tutor_obj: tutor.Tutor,
        assertions
):
    if not tutor_obj:
        return None
    learning_unit_acronyms_present_in_page = set([result.acronym.text for result in results])
    if not learning_unit_acronyms_present_in_page:
        return None
    expected_luys = LearningUnitYear.objects.filter(
        learning_container_year__attributionnew__tutor=tutor_obj
    )
    assertions.assertEqual(
        {luy.acronym for luy in expected_luys},
        learning_unit_acronyms_present_in_page
    )
