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

from features.steps.utils.pages import LearningUnitTrainingPage

use_step_matcher("re")


@when("Cliquer sur l'onglet Formations")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.current_page.tab_training.click()
    context.current_page = LearningUnitTrainingPage(context.browser, context.browser.current_url)


@then("Vérifier que l'unité d'enseignement est incluse dans (?P<list_acronym>.+)")
def step_impl(context, list_acronym):
    context.test.assertEqual(context.current_page.including_groups(), list_acronym.split(', '))


@then("Vérifier que (?P<acronym>.+) à la ligne (?P<nb_row>.+) a (?P<nb_training>.+) inscrits dont (?P<nb_luy>.+) à l'ue")
def step_impl(context, acronym, nb_row, nb_training, nb_luy):
    context.test.assertEqual(context.current_page.enrollments_row(nb_row), [acronym, nb_training, nb_luy])
