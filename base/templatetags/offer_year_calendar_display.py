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
from datetime import date


CURRENT_EVENT_CSS_STYLE = "font-weight:bold;"
NOT_CURRENT_EVENT_CSS_STYLE = ""

register = template.Library()


@register.filter
def offer_year_calendar_display(value_start, value_end):
    if value_start.date() and value_end.date():
        if value_start.date() <= date.today() <= value_end.date():
            return CURRENT_EVENT_CSS_STYLE
    return NOT_CURRENT_EVENT_CSS_STYLE
