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
import collections
import itertools

from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django_filters.views import FilterView

from base.business import learning_unit_year_with_context
from base.business.learning_unit_xls import create_xls, create_xls_with_parameters, WITH_GRP, WITH_ATTRIBUTIONS, \
    create_xls_attributions
from base.business.learning_units.xls_comparison import create_xls_comparison, create_xls_proposal_comparison
from base.business.proposal_xls import create_xls as create_xls_proposal
from base.forms.search.search_form import get_research_criteria
from base.templatetags import pagination
from base.views.common import remove_from_session

SIMPLE_SEARCH = 1
SERVICE_COURSES_SEARCH = 2
PROPOSAL_SEARCH = 3
SUMMARY_LIST = 4
BORROWED_COURSE = 5
EXTERNAL_SEARCH = 6


def _manage_session_variables(request, search_type):
    remove_from_session(request, 'search_url')
    if search_type == 'EXTERNAL':
        request.session['ue_search_type'] = str(_('External learning units'))
    elif search_type == SIMPLE_SEARCH:
        request.session['ue_search_type'] = None
    else:
        request.session['ue_search_type'] = str(_get_search_type_label(search_type))


def _get_filter(form, search_type):
    criterias = itertools.chain([(_('Search type'), _get_search_type_label(search_type))], get_research_criteria(form))
    return collections.OrderedDict(criterias)


def _get_search_type_label(search_type):
    return {
        PROPOSAL_SEARCH: _('Proposals'),
        SERVICE_COURSES_SEARCH: _('Service courses'),
        BORROWED_COURSE: _('Borrowed courses')
    }.get(search_type, _('Learning units'))


class SearchMixin:
    """
        Search Mixin to return FilterView filter result as json when request is of type ajax.
        Also implements method to return number of items per page.

        serializer_class: class used to serialize the resulting queryset
    """
    serializer_class = None

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            serializer = self.serializer_class(context["page_obj"], context={'request': self.request}, many=True)
            return JsonResponse({'object_list': serializer.data})
        return super().render_to_response(context, **response_kwargs)

    def get_paginate_by(self, queryset):
        pagination.store_paginator_size(self.request)
        return pagination.get_paginator_size(self.request)


class RenderToExcel:
    """
        View Mixin to generate excel when xls_status parameter is set.

        name: value of xls_status so as to generate the excel
        render_method: function to generate the excel.
                       The function must have as signature f(view_obj, context, **response_kwargs)
    """
    def __init__(self, name, render_method):
        self.name = name
        self.render_method = render_method

    def __call__(self, filter_class: FilterView):
        class Wrapped(filter_class):
            def render_to_response(obj, context, **response_kwargs):
                if obj.request.GET.get('xls_status') == self.name:
                    return self.render_method(obj, context, **response_kwargs)
                return super().render_to_response(context, **response_kwargs)
        return Wrapped


def _create_xls(view_obj, context, **response_kwargs):
    user = view_obj.request.user
    luys = context["filter"].qs
    filters = _get_filter(context["form"], view_obj.search_type)
    return create_xls(user, luys, filters)


def _create_xls_comparison(view_obj, context, **response_kwargs):
    user = view_obj.request.user
    luys = context["filter"].qs
    filters = _get_filter(context["form"], view_obj.search_type)
    comparison_year = view_obj.request.POST.get('comparison_year')
    return create_xls_comparison(user, luys, filters, comparison_year)


def _create_xls_with_parameters(view_obj, context, **response_kwargs):
    user = view_obj.request.user
    luys = context["filter"].qs
    filters = _get_filter(context["form"], view_obj.search_type)
    other_params = {
        WITH_GRP: view_obj.request.POST.get('with_grp') == 'true',
        WITH_ATTRIBUTIONS: view_obj.request.POST.get('with_attributions') == 'true'
    }
    return create_xls_with_parameters(user, luys, filters, other_params)


def _create_xls_attributions(view_obj, context, **response_kwargs):
    user = view_obj.request.user
    luys = context["filter"].qs
    filters = _get_filter(context["form"], view_obj.search_type)
    return create_xls_attributions(user, luys, filters)


def _create_xls_proposal(view_obj, context, **response_kwargs):
    user = view_obj.request.user
    luys = context["filter"].qs
    filters = _get_filter(context["form"], view_obj.search_type)
    return create_xls_proposal(user, luys, filters)


def _create_xls_proposal_comparison(view_obj, context, **response_kwargs):
    user = view_obj.request.user
    luys = context["filter"].qs
    for luy in luys:
        learning_unit_year_with_context.append_latest_entities(luy, service_course_search=False)
    filters = _get_filter(context["form"], view_obj.search_type)
    return create_xls_proposal_comparison(user, luys, filters)
