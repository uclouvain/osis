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
from selenium.webdriver.common.by import By

from base.business.education_groups.create import create_initial_group_element_year_structure
from base.models.education_group_type import EducationGroupType
from base.models.entity import Entity
from base.models.enums.education_group_types import TrainingType
from base.tests.factories.education_group_year import TrainingFactory

use_step_matcher("parse")


@step("La formation {acronym} doit exister")
def step_impl(context, acronym):
    """
    :type context: behave.runner.Context
    """
    entity = Entity.objects.filter(entityversion__acronym='DRT').first()

    training = TrainingFactory(
        acronym=acronym,
        partial_acronym='LDROI200S',
        education_group_type=EducationGroupType.objects.get(name=TrainingType.MASTER_MS_120.name),
        academic_year__year=2018,
        management_entity=entity,
        administration_entity=entity
    )
    create_initial_group_element_year_structure([training])


@step("Cliquer sur le sigle {acronym} dans la liste de résultats")
def step_impl(context, acronym):
    """
    :type context: behave.runner.Context
    """
    context.current_page = context.current_page.first_row.click()


@step("Cliquer sur « Supprimer »")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.current_page.delete.click()


@then("Vérifier que la liste est vide.")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    warnings = context.current_page.find_element(By.ID, 'pnl_warning_messages').text
    context.test.assertIn('Aucun résultat!', warnings)
