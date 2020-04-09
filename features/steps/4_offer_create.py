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
import random
from behave import *
from behave.runner import Context
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from waffle.models import Flag

from base.models.entity_version import EntityVersion
from base.models.enums.entity_type import FACULTY
from base.tests.factories.education_group_year import string_generator
from features.pages.education_group.pages import SearchEducationGroupPage, UpdateTrainingPage

use_step_matcher("parse")


@step("les flags d'éditions des offres sont désactivés.")
def step_impl(context: Context):
    Flag.objects.update_or_create(name='education_group_create', defaults={"authenticated": True})
    Flag.objects.update_or_create(name='education_group_delete', defaults={"authenticated": True})
    Flag.objects.update_or_create(name='education_group_update', defaults={"authenticated": True})


@given("Aller sur la page Catalogue de formations / Formation")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    url = '/educationgroups/'
    context.current_page = SearchEducationGroupPage(driver=context.browser, base_url=context.get_url(url)).open()
    context.test.assertEqual(context.browser.current_url, context.get_url(url))


@step("Cliquer sur « Nouvelle Formation »")
def step_impl(context):
    context.current_page.new_training.click()


@step("Cliquer sur « Oui, je confirme »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.current_page = context.current_page.confirm_modal.click()


@step("Cliquer sur l'onglet Diplômes/Certificats")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.current_page.tab_diploma.click()


@step("Si une modal d'avertissement s'affiche, cliquer sur « oui »")
def step_impl(context: Context):
    try:
        page = UpdateTrainingPage(driver=context.browser)
        page.find_element(
            By.CSS_SELECTOR,
            '#confirm-modal > div > div > div.modal-footer > button.btn.btn-warning'
        ).click()
    except NoSuchElementException:
        pass


@then("Vérifier que la formation {acronym} à bien été créée de {start_year} à {end_year}")
def step_impl(context, acronym, start_year, end_year):
    """
    :type context: behave.runner.Context
    """
    for i in range(int(start_year), int(end_year) + 1):
        string_to_check = "{} ({}-".format(acronym, i)
        context.test.assertIn(string_to_check, context.current_page.success_messages.text)


@then("Vérifier que la formation {acronym} à bien été créée")
def step_impl(context, acronym):
    string_to_check = "créée avec succès"
    context.test.assertIn(string_to_check, context.current_page.success_messages.text)


@step("Cliquer sur « Nouvelle Mini-Formation »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.current_page.new_mini_training.click()


@when("Ouvrir l'arbre")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.current_page.toggle_tree.click()


@then("Vérifier que le(s) enfant(s) de {code} sont bien {children}")
def step_impl(context, code, children):
    """
    :type context: behave.runner.Context
    :type code: str
    :type children: str
    """
    context.current_page.open_first_node_tree.click()

    expected_children = children.split(',')
    children_in_tree = context.current_page.get_name_first_children()
    for i, child in enumerate(expected_children):
        context.test.assertIn(child, children_in_tree[i])


@step("Encoder Entité de gestion")
def step_impl(context: Context):
    ev = EntityVersion.objects.get(entity__personentity__person=context.user.person)
    entities_version = [ev] + list(ev.descendants)
    faculties = [ev for ev in entities_version if ev.entity_type == FACULTY]
    random_entity_version = random.choice(faculties)
    context.current_page.entite_de_gestion = random_entity_version.acronym


@step("Encoder Entité d’administration")
def step_impl(context: Context):
    entities_version = EntityVersion.objects.get(entity__personentity__person=context.user.person).descendants
    faculties = [ev for ev in entities_version if ev.entity_type == FACULTY]
    random_entity_version = random.choice(faculties)
    context.current_page.entite_dadministration = random_entity_version.acronym


@step("Encoder intitulé français")
def step_impl(context: Context):
    title = string_generator()
    context.current_page.intitule_en_francais = title


@step("Encoder intitulé anglais")
def step_impl(context: Context):
    title = string_generator()
    context.current_page.intitule_en_anglais = title
