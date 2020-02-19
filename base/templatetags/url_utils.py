############################################################################
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
############################################################################
import urllib

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_params(context, *args, **kwargs):
    kwargs_without_none_values = {key: value for key, value in kwargs.items() if value is not None}
    query_parameters = _get_existing_query_parameters(context)
    query_parameters.update(kwargs_without_none_values)
    if query_parameters:
        return "?{parameters}".format(parameters=urllib.parse.urlencode(query_parameters))
    return ""


def _get_existing_query_parameters(context):
    request = context.get("request")
    if request:
        return request.GET.dict()
    return {}
