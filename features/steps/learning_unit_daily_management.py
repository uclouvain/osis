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
from django.utils.text import slugify
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base.models.entity import Entity
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.person import FacultyManagerFactory, CentralManagerFactory
from base.tests.factories.person_entity import PersonEntityFactory
from features.steps.utils import LearningUnitPage, LoginPage, LearningUnitEditPage

use_step_matcher("re")


@step("La période de modification des programmes est en cours")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    # FIXME
    pass


@step("L’utilisateur est dans le groupe « faculty manager »")
def step_impl(context: Context):
    person = FacultyManagerFactory(
        user__username="usual_suspect",
        user__first_name="Keyser",
        user__last_name="Söze",
        user__password="Roger_Verbal_Kint"
    )

    context.user = person.user

    page = LoginPage(driver=context.browser, base_url=context.get_url('/login/')).open()
    page.login("usual_suspect", 'Roger_Verbal_Kint')

    context.test.assertEqual(context.browser.current_url, context.get_url('/'))


@step("L’utilisateur est attaché à l’entité DRT")
def step_impl(context: Context):
    drt_faculty = Entity.objects.filter(entityversion__acronym='DRT').first()
    PersonEntityFactory(person=context.user.person, entity=drt_faculty, with_child=True)


@when("Cliquer sur le menu « Actions »")
def step_impl(context: Context):
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


@step("Cliquer sur le menu « Modifier »")
def step_impl(context):
    context.current_page.edit_button.click()
    context.current_page = LearningUnitEditPage(context.browser, context.browser.current_url)


@step("Décocher la case « Actif »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.current_page.actif = False


@step("Encoder (?P<value>.+) comme (?P<field>.+)")
def step_impl(context: Context, value: str, field: str):
    slug_field = slugify(field).replace('-', '_')
    setattr(context.current_page, slug_field, value)


@step("Cliquer sur le bouton « Enregistrer »")
def step_impl(context: Context):
    context.current_page.save_button.click()


@step("A la question, « voulez-vous reporter » répondez « non »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.current_page.no_postponement.click()
    # Slow page...
    WebDriverWait(context.browser, 10).until(
        EC.presence_of_element_located((By.ID, "id_acronym"))
    )

    context.current_page = LearningUnitPage(context.browser, context.browser.current_url)


@then("Vérifier que le cours est bien (?P<status>.+)")
def step_impl(context: Context, status: str):
    context.test.assertEqual(context.current_page.find_element(By.ID, "id_status").text, status)


@step("Vérifier que le Quadrimestre est bien (?P<value>.+)")
def step_impl(context: Context, value: str):
    context.test.assertEqual(context.current_page.find_element(By.ID, "id_quadrimester").text, value)


@step("Vérifier que la Session dérogation est bien (?P<value>.+)")
def step_impl(context: Context, value: str):
    context.test.assertEqual(context.current_page.find_element(By.ID, "id_session").text, value)


@step("Vérifier que le volume Q1 pour la partie magistrale est bien (?P<value>.+)")
def step_impl(context: Context, value: str):
    context.test.assertEqual(context.current_page.find_element(
        By.XPATH,
        '//*[@id="identification"]/div/div[1]/div[3]/div/table/tbody/tr[1]/td[3]'
    ).text, value)


@step("Vérifier que le volume Q2 pour la partie magistrale est bien (?P<value>.+)")
def step_impl(context: Context, value: str):
    context.test.assertEqual(context.current_page.find_element(
        By.XPATH,
        '//*[@id="identification"]/div/div[1]/div[3]/div/table/tbody/tr[1]/td[4]'
    ).text, value)


@step("Vérifier que le volume Q1 pour la partie pratique est bien (?P<value>.+)")
def step_impl(context: Context, value: str):
    context.test.assertEqual(context.current_page.find_element(
        By.XPATH,
        '//*[@id="identification"]/div/div[1]/div[3]/div/table/tbody/tr[2]/td[3]'
    ).text, value)


@step("Vérifier que la volume Q2 pour la partie pratique est bien (?P<value>.+)")
def step_impl(context: Context, value: str):
    context.test.assertEqual(context.current_page.find_element(
        By.XPATH,
        '//*[@id="identification"]/div/div[1]/div[3]/div/table/tbody/tr[2]/td[4]'
    ).text, value)


@given("La période de modification des programmes n’est pas en cours")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    # TODO
    pass


@step("L’utilisateur est dans le groupe « central manager »")
def step_impl(context):
    person = CentralManagerFactory(
        user__username="usual_suspect",
        user__first_name="Keyser",
        user__last_name="Söze",
        user__password="Roger_Verbal_Kint"
    )

    context.user = person.user

    page = LoginPage(driver=context.browser, base_url=context.get_url('/login/')).open()
    page.login("usual_suspect", 'Roger_Verbal_Kint')

    context.test.assertEqual(context.browser.current_url, context.get_url('/'))


@step("A la question, « voulez-vous reporter » répondez « oui »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.current_page.with_postponement.click()
    # Slow page...
    WebDriverWait(context.browser, 10).until(
        EC.presence_of_element_located((By.ID, "id_acronym"))
    )

    context.current_page = LearningUnitPage(context.browser, context.browser.current_url)


@then("Vérifier que le Crédits est bien (?P<value>.+)")
def step_impl(context, value):
    context.test.assertEqual(context.current_page.find_element(By.ID, "id_credits").text, value)


@step("Vérifier que la Périodicité est bien (?P<value>.+)")
def step_impl(context, value):
    context.test.assertEqual(context.current_page.find_element(By.ID, "id_periodicity").text, value)


@step("Rechercher (?P<acronym>.+) en 2020-21")
def step_impl(context, acronym):
    luy = LearningUnitYear.objects.get(acronym=acronym, academic_year__year=2020)
    url = reverse('learning_unit', args=[luy.pk])

    context.current_page = LearningUnitPage(driver=context.browser, base_url=context.get_url(url)).open()
    context.test.assertEqual(context.browser.current_url, context.get_url(url))
