##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django import template

DISABLED = 'disabled'
ENABLED = ''
register = template.Library()


@register.simple_tag(takes_context=True)
def get_score_justification_disabled_status(context):
    enrollment = context["enrollment"]
    is_program_manager = context["is_program_manager"]

    is_deadline_reached_for_program_manager = enrollment.deadline_reached
    is_deadline_reached_for_tutor = enrollment.deadline_reached or enrollment.deadline_tutor_reached
    is_final_score_encoded = enrollment.score_final or enrollment.score_final == 0 or enrollment.justification_final

    if enrollment.enrollment_state != 'ENROLLED':
        return DISABLED
    elif is_program_manager and is_deadline_reached_for_program_manager:
        return DISABLED
    elif not is_program_manager and (is_final_score_encoded or is_deadline_reached_for_tutor):
        return DISABLED

    return ENABLED
