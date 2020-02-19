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

from django.http import QueryDict
from django.template.defaulttags import register
from django.urls import reverse

from base.forms.education_groups import EducationGroupFilter


@register.inclusion_tag('templatetags/navigation.html', takes_context=False)
def navigation(query_parameters: QueryDict, current_element):
    search_query_string = query_parameters.get("search_query")
    index = query_parameters.get("index")
    context = {"current_element": current_element}
    if search_query_string and index is not None:
        unquoted_search_query_string = urllib.parse.unquote_plus(search_query_string)
        context.update(update_context_with_navigation_elements(query_parameters, unquoted_search_query_string, int(index)))
    return context


def update_context_with_navigation_elements(query_parameters, search_query_string, index,):
    search_parameters = QueryDict(search_query_string).dict()
    qs = EducationGroupFilter(data=search_parameters).qs
    context = {}
    context["next_element"] = get_next_element(qs, index)
    context["next_url"] = create_url(context["next_element"], query_parameters, index + 1) if context["next_element"] else None
    context["previous_element"] = get_previous_element(qs, index)
    context["previous_url"] = create_url(context["previous_element"], query_parameters, index - 1) if context["previous_element"] else None
    return context


def get_next_element(qs, index):
    try:
        return qs[index + 1] if index >= 0 else None
    except IndexError:
        return None


def get_previous_element(qs, index):
    try:
        return qs[index - 1] if index > 0 else None
    except IndexError:
        return None


def create_url(education_group_year, query_parameters: QueryDict, index):
    new_parameters = QueryDict(mutable=True)
    new_parameters.update(query_parameters)
    new_parameters["index"] = index
    return "{}?{}".format(
        reverse("education_group_read", args=[education_group_year.id, education_group_year.id]),
        new_parameters.urlencode()
    )
