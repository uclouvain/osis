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

from base.models.entity import Entity
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory

use_step_matcher("parse")


@step("Les propositions {proposals} doivent être attachées à {entity} en {year}")
def step_impl(context, proposals, entity, year):
    """
    :type context: behave.runner.Context
    """
    entity = Entity.objects.filter(entityversion__acronym=entity).last()
    for acronym in proposals.split(','):
        luy = LearningUnitYearFactory(acronym=acronym, academic_year__year=int(year[:4]))
        ProposalLearningUnitFactory(learning_unit_year=luy,
                                    entity=entity,
                                    folder_id=12)
