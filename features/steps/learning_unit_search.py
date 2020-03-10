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

from base.models.education_group_type import EducationGroupType
from base.models.entity_version import EntityVersion
from base.models.enums import education_group_categories
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.learning_unit_year import LearningUnitYear
from base.models.tutor import Tutor
from base.tests.factories.education_group_type import MiniTrainingEducationGroupTypeFactory
from features.pages.learning_unit.pages import SearchLearningUnitPage

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
    acronyms_results = [result.acronym.text for result in context.current_page.proposal_results]
    print(acronyms_results)
    for row, acronym in enumerate(acronyms):
        context.test.assertTrue(acronym in acronyms_results)


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


@step("Sélectionner l’onglet « Propositions »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.current_page = context.current_page.proposal_search.click()


@step("Encoder le code d'une UE")
def step_impl(context: Context):
    context.learning_unit_year_to_research = LearningUnitYear.objects.all().order_by("?").first()
    setattr(context.current_page, "acronym", context.learning_unit_year_to_research.acronym)


@step("Encoder le type d'UE")
def step_impl(context: Context):
    context.type_to_search = random.choice(LearningContainerYearType.get_values())
    setattr(context.current_page, "container_type", context.type_to_search)


@step("Encoder l'entité d'UE")
def step_impl(context: Context):
    context.entity_to_search = EntityVersion.objects.all().order_by("?").first()
    setattr(context.current_page, "requirement_entity", context.entity_to_search.acronym)


@step("Encoder l'enseignant d'UE")
def step_impl(context: Context):
    context.tutor_to_search = Tutor.objects.all().order_by("?").first()
    setattr(context.current_page, "tutor", context.tutor_to_search.person.full_name)


@step("Dans la liste de résultat, l'UE doit apparaître")
def step_impl(context: Context):
    context.test.assertIn(
        context.learning_unit_year_to_research.acronym,
        [result.acronym.text for result in context.current_page.results]
    )


@step("Dans la liste de résultat, seul ce type doit apparaître")
def step_impl(context: Context):
    learning_unit_types_present_in_page = set([result.type.text for result in context.current_page.results])
    context.test.assertEqual(
        {context.type_to_search},
        learning_unit_types_present_in_page
    )


@step("Dans la liste de résultat, seul cette entité doit apparaître")
def step_impl(context: Context):
    learning_unit_entities_present_in_page = set([result.requirement_entity.text for result in context.current_page.results])
    if not learning_unit_entities_present_in_page:
        return None
    expected_entities = [context.entity_to_search] + list(context.entity_to_search.descendants)
    context.test.assertTrue(
        {e.acronym for e in expected_entities} >= learning_unit_entities_present_in_page
    )


@step("Dans la liste de résultat, seul les UEs de l'enseignant doivent apparaître")
def step_impl(context: Context):
    learning_unit_acronyms_present_in_page = set([result.acronym.text for result in context.current_page.results])
    if not learning_unit_acronyms_present_in_page:
        return None
    expected_luys = LearningUnitYear.objects.filter(
        learning_container_year__attributionnew__tutor=context.tutor_to_search
    )
    context.test.assertEqual(
        {luy.acronym for luy in expected_luys},
        learning_unit_acronyms_present_in_page
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
