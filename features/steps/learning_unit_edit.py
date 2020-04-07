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
import time
from datetime import datetime, timedelta

from behave import *
from behave.runner import Context
from django.urls import reverse
from django.utils.text import slugify
from selenium.webdriver.common.by import By
from waffle.models import Flag

from base.models.academic_calendar import AcademicCalendar
from base.models.academic_year import current_academic_year, AcademicYear
from base.models.campus import Campus
from base.models.entity_version import EntityVersion
from base.models.enums.academic_calendar_type import EDUCATION_GROUP_EDITION
from base.models.enums.entity_type import FACULTY
from base.models.learning_unit_year import LearningUnitYear
from features.forms.learning_units import update_form, create_form
from features.pages.learning_unit.pages import LearningUnitPage, LearningUnitEditPage, NewLearningUnitProposalPage, \
    SearchLearningUnitPage, NewPartimPage, NewLearningUnitPage, EditLearningUnitProposalPage
from django.utils.translation import gettext_lazy as _

use_step_matcher("parse")


@when("Cliquer sur le menu « Actions »")
def step_impl(context: Context):
    page = LearningUnitPage(driver=context.browser)
    page.actions.click()


@when("Cliquer sur le menu « Actions » depuis la recherche")
def step_impl(context: Context):
    page = SearchLearningUnitPage(driver=context.browser)
    page.actions.click()


@then("L’action « Modifier » est désactivée.")
def step_impl(context: Context):
    page = LearningUnitPage(driver=context.browser)
    context.test.assertTrue(page.is_li_edit_link_disabled())


@given("Aller sur la page de detail d'une UE ne faisant pas partie de la faculté")
def step_impl(context: Context):
    entities_version = EntityVersion.objects.get(entity__personentity__person=context.user.person).descendants
    entities = [ev.entity for ev in entities_version]
    luy = LearningUnitYear.objects.exclude(learning_container_year__requirement_entity__in=entities).order_by("?")[0]
    url = reverse('learning_unit', args=[luy.pk])

    LearningUnitPage(driver=context.browser, base_url=context.get_url(url)).open()


@given("Aller sur la page de detail d'une UE faisant partie de la faculté")
def step_impl(context: Context):
    entities_version = EntityVersion.objects.get(entity__personentity__person=context.user.person).descendants
    entities = [ev.entity for ev in entities_version]
    luy = LearningUnitYear.objects.filter(
        learning_container_year__requirement_entity__in=entities,
        academic_year=current_academic_year()
    ).order_by("?")[0]
    context.learning_unit_year = luy
    url = reverse('learning_unit', args=[luy.pk])

    LearningUnitPage(driver=context.browser, base_url=context.get_url(url)).open()


@given("Aller sur la page de detail d'une UE faisant partie de la faculté l'année suivante")
def step_impl(context: Context):
    entities_version = EntityVersion.objects.get(entity__personentity__person=context.user.person).descendants
    entities = [ev.entity for ev in entities_version]
    luy = LearningUnitYear.objects.filter(
        learning_container_year__requirement_entity__in=entities,
        academic_year__year=current_academic_year().year + 1
    ).order_by("?")[0]
    context.learning_unit_year = luy
    url = reverse('learning_unit', args=[luy.pk])

    LearningUnitPage(driver=context.browser, base_url=context.get_url(url)).open()


@then("L’action « Modifier » est activée.")
def step_impl(context: Context):
    page = LearningUnitPage(driver=context.browser)
    context.test.assertFalse(page.is_li_edit_link_disabled())


@step("Cliquer sur le menu « Modifier »")
def step_impl(context):
    page = LearningUnitPage(driver=context.browser)
    page.edit_button.click()


@step("Décocher la case « Actif »")
def step_impl(context: Context):
    page = LearningUnitEditPage(driver=context.browser)
    page.actif = False


@step("Le gestionnaire faculatire remplit le formulaire d'édition des UE")
def step_impl(context: Context):
    page = LearningUnitEditPage(driver=context.browser)
    context.form_data = update_form.fill_form_for_faculty(page)


@step("Le gestionnaire faculatire remplit le formulaire de création de partim")
def step_impl(context: Context):
    page = NewPartimPage(driver=context.browser)
    context.form_data = create_form.fill_partim_form_for_faculty_manager(page)


@step("Le gestionnaire central remplit le formulaire de création d'autre collectif")
def step_impl(context: Context):
    page = NewLearningUnitPage(driver=context.browser)
    context.form_data = create_form.fill_other_collective_form_for_central_manager(page, context.user.person)


@step("Le gestionnaire central remplit le formulaire d'édition des UE")
def step_impl(context: Context):
    page = LearningUnitEditPage(driver=context.browser)
    context.form_data = update_form.fill_form_for_central(page)


@step("Vérifier UE a été mis à jour")
def step_impl(context: Context):
    page = LearningUnitPage(driver=context.browser)
    assert_actif_equal(context.test, context.form_data["actif"], page.status.text)
    assert_choice_equal(context.test, page.session_derogation.text, context.form_data["session_derogation"])
    assert_choice_equal(context.test, page.quadrimester.text, context.form_data["quadrimester"])
    if "credits" in context.form_data:
        context.test.assertEqual(context.form_data["credits"], int(page.credits.text))
    if "periodicity" in context.form_data:
        assert_choice_equal(context.test, page.periodicity, context.form_data["periodicity"])


def assert_choice_equal(assertions, display_value, input_value):
    expected_value = input_value if input_value != '---------' else '-'
    assertions.assertEqual(display_value, expected_value)


def assert_actif_equal(assertions, status_boolean_value, status_text_value):
    status_expected_value = _("Active") if status_boolean_value else _("Inactive")
    assertions.assertEqual(status_text_value, status_expected_value)


@step("Encoder pour le partim {value} comme {field}")
def step_impl(context: Context, value: str, field: str):
    page = NewPartimPage(driver=context.browser)
    slug_field = slugify(field).replace('-', '_')
    if hasattr(page, slug_field):
        setattr(page, slug_field, value)
    else:
        raise AttributeError(page.__class__.__name__ + " has no " + slug_field)


@step("Encoder pour nouvelle UE {value} comme {field}")
def step_impl(context: Context, value: str, field: str):
    page = NewLearningUnitPage(driver=context.browser)
    slug_field = slugify(field).replace('-', '_')
    if hasattr(page, slug_field):
        setattr(page, slug_field, value)
    else:
        raise AttributeError(page.__class__.__name__ + " has no " + slug_field)


@step("Encoder {value} comme {field}")
def step_impl(context: Context, value: str, field: str):
    page = LearningUnitEditPage(driver=context.browser)
    slug_field = slugify(field).replace('-', '_')
    if hasattr(page, slug_field):
        setattr(page, slug_field, value)
    else:
        raise AttributeError(page.__class__.__name__ + " has no " + slug_field)


@step("Recherche proposition Encoder {value} comme {field}")
def step_impl(context: Context, value: str, field: str):
    page = SearchLearningUnitPage(driver=context.browser)
    slug_field = slugify(field).replace('-', '_')
    if hasattr(page, slug_field):
        setattr(page, slug_field, value)
    else:
        raise AttributeError(page.__class__.__name__ + " has no " + slug_field)


@step("Proposition Encoder {value} comme {field}")
def step_impl(context: Context, value: str, field: str):
    page = EditLearningUnitProposalPage(driver=context.browser)
    slug_field = slugify(field).replace('-', '_')
    if hasattr(page, slug_field):
        setattr(page, slug_field, value)
    else:
        raise AttributeError(page.__class__.__name__ + " has no " + slug_field)


@step("Encoder année suivante")
def step_impl(context: Context):
    page = LearningUnitEditPage(driver=context.browser)
    year = current_academic_year().year + 1
    page.anac = str(AcademicYear.objects.get(year=year))


@step("Encoder Anac de fin supérieure")
def step_impl(context: Context):
    page = LearningUnitEditPage(driver=context.browser)
    current_acy = current_academic_year()
    academic_year = AcademicYear.objects.filter(year__gt=current_acy.year, year__lt=current_acy.year+6).order_by("?")[0]
    context.anac = academic_year
    page.anac_de_fin = str(academic_year)


@step("Encoder Dossier")
def step_impl(context: Context):
    page = NewLearningUnitProposalPage(driver=context.browser)
    entities_version = EntityVersion.objects.get(entity__personentity__person=context.user.person).descendants
    faculties = [ev for ev in entities_version if ev.entity_type == FACULTY]
    random_entity_version = random.choice(faculties)
    value = "{}12".format(random_entity_version.acronym)
    page.dossier = value


@step("Encoder Lieu d’enseignement")
def step_impl(context: Context):
    page = LearningUnitEditPage(driver=context.browser)
    random_campus = Campus.objects.all().order_by("?")[0]
    page.lieu_denseignement = random_campus.id


@step("Encoder Entité resp. cahier des charges")
def step_impl(context: Context):
    page = LearningUnitEditPage(driver=context.browser)
    ev = EntityVersion.objects.get(entity__personentity__person=context.user.person)
    entities_version = [ev] + list(ev.descendants)
    faculties = [ev for ev in entities_version if ev.entity_type == FACULTY]
    random_entity_version = random.choice(faculties)
    page.entite_resp_cahier_des_charges = random_entity_version.acronym


@step("Encoder Entité d’attribution")
def step_impl(context: Context):
    page = LearningUnitEditPage(driver=context.browser)
    entities_version = EntityVersion.objects.get(entity__personentity__person=context.user.person).descendants
    faculties = [ev for ev in entities_version if ev.entity_type == FACULTY]
    random_entity_version = random.choice(faculties)
    page.entite_dattribution = random_entity_version.acronym


@step("Cliquer sur le bouton « Enregistrer »")
def step_impl(context: Context):
    page = LearningUnitEditPage(driver=context.browser)
    page.save_button.click()


@step("Proposition Cliquer sur le bouton « Enregistrer »")
def step_impl(context: Context):
    page = EditLearningUnitProposalPage(driver=context.browser)
    page.save_button.click()


@step("Cliquer sur le bouton « Enregistrer » de la création")
def step_impl(context: Context):
    page = NewLearningUnitPage(driver=context.browser)
    page.save_button.click()


@step("Cliquer sur le bouton « Enregistrer » pour partim")
def step_impl(context: Context):
    page = NewPartimPage(driver=context.browser)
    page.save_button.click()


@step("A la question, « voulez-vous reporter » répondez « non »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    page = LearningUnitEditPage(driver=context.browser)
    page.no_postponement.click()


@then("Vérifier que le cours est bien {status}")
def step_impl(context: Context, status: str):
    page = LearningUnitPage(driver=context.browser)
    context.test.assertEqual(page.find_element(By.ID, "id_status").text, status)


@step("Vérifier que le Quadrimestre est bien {value}")
def step_impl(context: Context, value: str):
    page = LearningUnitPage(driver=context.browser)
    context.test.assertEqual(page.find_element(By.ID, "id_quadrimester").text, value)


@step("Vérifier que la Session dérogation est bien {value}")
def step_impl(context: Context, value: str):
    page = LearningUnitPage(driver=context.browser)
    context.test.assertEqual(page.find_element(By.ID, "id_session").text, value)


@step("Vérifier que le volume Q1 pour la partie magistrale est bien {value}")
def step_impl(context: Context, value: str):
    page = LearningUnitPage(driver=context.browser)
    context.test.assertEqual(page.find_element(
        By.XPATH,
        '//*[@id="identification"]/div/div[1]/div[3]/div/table/tbody/tr[1]/td[3]'
    ).text, value)


@step("Vérifier que le volume Q2 pour la partie magistrale est bien {value}")
def step_impl(context: Context, value: str):
    page = LearningUnitPage(driver=context.browser)
    context.test.assertEqual(page.find_element(
        By.XPATH,
        '//*[@id="identification"]/div/div[1]/div[3]/div/table/tbody/tr[1]/td[4]'
    ).text, value)


@step("Vérifier que le volume Q1 pour la partie pratique est bien {value}")
def step_impl(context: Context, value: str):
    page = LearningUnitPage(driver=context.browser)
    context.test.assertEqual(page.find_element(
        By.XPATH,
        '//*[@id="identification"]/div/div[1]/div[3]/div/table/tbody/tr[2]/td[3]'
    ).text, value)


@step("Vérifier que la volume Q2 pour la partie pratique est bien {value}")
def step_impl(context: Context, value: str):
    page = LearningUnitPage(driver=context.browser)
    context.test.assertEqual(page.find_element(
        By.XPATH,
        '//*[@id="identification"]/div/div[1]/div[3]/div/table/tbody/tr[2]/td[4]'
    ).text, value)


@given("La période de modification des programmes n’est pas en cours")
def step_impl(context: Context):
    calendar = AcademicCalendar.objects.filter(academic_year=current_academic_year(),
                                               reference=EDUCATION_GROUP_EDITION).first()
    if calendar:
        calendar.end_date = (datetime.now() - timedelta(days=1)).date()
        calendar.save()


@step("A la question, « voulez-vous reporter » répondez « oui »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    page = LearningUnitEditPage(driver=context.browser)
    context.current_page = page.with_postponement.click()


@then("Vérifier que le champ {field} est bien {value}")
def step_impl(context, field, value):
    page = LearningUnitPage(driver=context.browser)
    slug_field = slugify(field).replace('-', '_')
    context.test.assertIn(value, getattr(page, slug_field).text)


@step("Vérifier que la Périodicité est bien {value}")
def step_impl(context, value):
    page = LearningUnitPage(driver=context.browser)
    context.test.assertEqual(page.find_element(By.ID, "id_periodicity").text, value)


@step("Rechercher la même UE dans une année supérieure")
def step_impl(context: Context):
    luy = LearningUnitYear.objects.filter(
        learning_unit=context.learning_unit_year.learning_unit,
        academic_year__year__gt=context.learning_unit_year.academic_year.year
    ).first()
    url = reverse('learning_unit', args=[luy.pk])

    LearningUnitPage(driver=context.browser, base_url=context.get_url(url)).open()


@step("Cliquer sur le menu « Nouveau partim »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    page = LearningUnitPage(driver=context.browser)
    context.current_page = page.new_partim.click()


@then("Vérifier que le partim {acronym} a bien été créé de 2019-20 à 2024-25.")
def step_impl(context, acronym: str):
    page = LearningUnitPage(context.browser, context.browser.current_url)
    page.wait_for_page_to_load()
    for i in range(2019, 2025):
        string_to_check = "{} ({}-".format(acronym, i)
        context.test.assertIn(string_to_check, page.success_messages.text)


@then("Vérifier que l'UE a bien été créé")
def step_impl(context):
    page = LearningUnitPage(context.browser, context.browser.current_url)
    context.test.assertEqual(page.code.text, context.form_data["code"])


@then("Vérifier que le partim a bien été créé de 2019-20 à 2024-25.")
def step_impl(context):
    page = LearningUnitPage(context.browser, context.browser.current_url)
    page.wait_for_page_to_load()
    for i in range(2019, 2021):
        string_to_check = "{}3 ({}-".format(context.learning_unit_year.acronym, i)
        context.test.assertIn(string_to_check, page.success_messages.text)


@then("Vérifier que le partim a bien été créé")
def step_impl(context):
    page = LearningUnitPage(context.browser, context.browser.current_url)
    context.test.assertEqual(page.code.text[-1], context.form_data["partim_code"])


@when("Cliquer sur le lien {acronym}")
def step_impl(context: Context, acronym: str):
    page = LearningUnitPage(driver=context.browser)
    page.go_to_full.click()

    page = LearningUnitPage(context.browser, context.browser.current_url)
    page.wait_for_page_to_load()


@then("Vérifier que le cours parent {acronym} contient bien {number} partims.")
def step_impl(context, acronym, number):
    # Slow page...
    time.sleep(5)

    page = LearningUnitPage(driver=context.browser)
    list_partims = page.find_element(By.ID, "list_partims").text
    expected_string = ' , '.join([str(i + 1) for i in range(3)])
    context.test.assertEqual(list_partims, expected_string)


@step("Cliquer sur le menu « Nouvelle UE »")
def step_impl(context: Context):
    page = SearchLearningUnitPage(driver=context.browser)
    page.new_luy.click()


@step("les flags d'éditions des UEs sont désactivés.")
def step_impl(context: Context):
    Flag.objects.update_or_create(name='learning_achievement_update', defaults={"authenticated": True})
    Flag.objects.update_or_create(name='learning_unit_create', defaults={"authenticated": True})
    Flag.objects.update_or_create(name='learning_unit_proposal_create', defaults={"authenticated": True})


@then("la valeur de {field} est bien {value}")
def step_impl(context, field, value):
    """
    :type context: behave.runner.Context
    """
    page = LearningUnitPage(driver=context.browser)
    slug_field = slugify(field).replace('-', '_')
    msg = getattr(page, slug_field).text.strip()
    context.test.assertEqual(msg, value.strip())


@then("Vérifier que la zone {field} est bien grisée")
def step_impl(context, field):
    """
    :type context: behave.runner.Context
    """
    page = LearningUnitEditPage(driver=context.browser)
    slug_field = slugify(field).replace('-', '_')

    context.test.assertFalse(getattr(page, slug_field).is_enabled())
