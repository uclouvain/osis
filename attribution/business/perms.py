##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from base.models.learning_unit_year import LearningUnitYear
from osis_common.utils.perms import conjunction


def can_tutor_view_educational_information(user, learning_unit_year_id):
    return conjunction(
        _is_tutor_attributed_to_the_learning_unit
    )(user, learning_unit_year_id)


def _is_tutor_attributed_to_the_learning_unit(user, learning_unit_year_id):
    return LearningUnitYear.objects.filter(pk=learning_unit_year_id,  attribution__tutor__person__user=user).exists()
