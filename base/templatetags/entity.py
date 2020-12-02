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

from django import template

from base.models import entity_version
from base.models.enums.entity_container_year_link_type import REQUIREMENT_ENTITY

register = template.Library()


@register.filter
def requirement_entity(list, i):
    try:
        return list[int(i)].entities.get(REQUIREMENT_ENTITY).acronym
    except AttributeError:
        return ""


@register.filter
def entity_last_version(entity):
    try:
        return entity_version.get_last_version(entity).acronym
    except AttributeError:
        return None
