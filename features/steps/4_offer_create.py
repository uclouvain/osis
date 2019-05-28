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
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from features.steps.utils.pages import SearchEducationGroupPage

use_step_matcher("parse")


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
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    try:
        context.current_page.find_element(By.CSS_SELECTOR,
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
        context.test.assertIn(string_to_check, context.current_page.success_messages())


@step("Cliquer sur « Nouvelle Mini-Formation »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.current_page.new_mini_training.click()
