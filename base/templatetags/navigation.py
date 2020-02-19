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
from base.forms.learning_unit.search.simple import LearningUnitFilter


@register.inclusion_tag('templatetags/navigation.html', takes_context=False)
def navigation(query_parameters: QueryDict, current_element, url_name):
    context = {"current_element": current_element}

    search_query_string = query_parameters.get("search_query")
    index = query_parameters.get("index")
    if search_query_string and index is not None:
        unquoted_search_query_string = urllib.parse.unquote_plus(search_query_string)
        context.update(get_neighbor_elements(query_parameters, unquoted_search_query_string, int(index), url_name))

    return context


@register.inclusion_tag('templatetags/navigation.html', takes_context=False)
def navigation_lu(query_parameters: QueryDict, current_element, url_name):
    context = {"current_element": current_element}

    search_query_string = query_parameters.get("search_query")
    index = query_parameters.get("index")
    if search_query_string and index is not None:
        unquoted_search_query_string = urllib.parse.unquote_plus(search_query_string)
        context.update(get_neighbor_elements_lu(query_parameters, unquoted_search_query_string, int(index), url_name))

    return context


def get_neighbor_elements_lu(query_parameters, search_query_string, index, url_name):
    search_parameters = QueryDict(search_query_string).dict()
    qs = LearningUnitFilter(data=search_parameters).qs
    next_element = _get_next_element(qs, index)
    previous_element = _get_previous_element(qs, index)
    return {
        "next_element": next_element,
        "next_url": _create_url_lu(next_element, query_parameters, index + 1, url_name) if next_element else None,
        "previous_element": previous_element,
        "previous_url": _create_url_lu(previous_element, query_parameters, index - 1, url_name) if previous_element else None
    }


def get_neighbor_elements(query_parameters, search_query_string, index, url_name):
    search_parameters = QueryDict(search_query_string).dict()
    qs = EducationGroupFilter(data=search_parameters).qs
    next_element = _get_next_element(qs, index)
    previous_element = _get_previous_element(qs, index)
    return {
        "next_element": next_element,
        "next_url": _create_url(next_element, query_parameters, index + 1, url_name) if next_element else None,
        "previous_element": previous_element,
        "previous_url": _create_url(previous_element, query_parameters, index - 1, url_name) if previous_element else None
    }


def _get_next_element(qs, index):
    try:
        return qs[index + 1] if index >= 0 else None
    except IndexError:
        return None


def _get_previous_element(qs, index):
    try:
        return qs[index - 1] if index > 0 else None
    except IndexError:
        return None


def _create_url(education_group_year, query_parameters: QueryDict, index, url_name):
    query_parameters_with_udpated_index = QueryDict(mutable=True)
    query_parameters_with_udpated_index.update(query_parameters)
    query_parameters_with_udpated_index["index"] = index
    return "{}?{}".format(
        reverse(url_name, args=[education_group_year.id, education_group_year.id]),
        query_parameters_with_udpated_index.urlencode()
    )


def _create_url_lu(learning_unit_year, query_parameters: QueryDict, index, url_name):
    query_parameters_with_udpated_index = QueryDict(mutable=True)
    query_parameters_with_udpated_index.update(query_parameters)
    query_parameters_with_udpated_index["index"] = index
    return "{}?{}".format(
        reverse(url_name, args=[learning_unit_year.id]),
        query_parameters_with_udpated_index.urlencode()
    )
