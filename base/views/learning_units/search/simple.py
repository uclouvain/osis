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
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django_filters.views import FilterView

from base.business.learning_unit_xls import create_xls, create_xls_with_parameters, WITH_GRP, WITH_ATTRIBUTIONS, \
    create_xls_attributions
from base.business.learning_units.xls_comparison import create_xls_comparison, get_academic_year_of_reference
from base.forms.learning_unit.comparison import SelectComparisonYears
from base.forms.learning_unit.search_form import LearningUnitFilter
from base.models.academic_year import starting_academic_year
from base.models.learning_unit_year import LearningUnitYear
from base.utils.cache import cache_filter, CacheFilterMixin
from base.views.common import paginate_queryset
from base.views.learning_units.search.common import SIMPLE_SEARCH, _get_filter, \
    ITEMS_PER_PAGES
from learning_unit.api.serializers.learning_unit import LearningUnitSerializer


# TODO login required
class LearningUnitSearch(PermissionRequiredMixin, CacheFilterMixin, FilterView):
    model = LearningUnitYear
    paginate_by = 2000
    template_name = "learning_unit/search/simple.html"
    raise_exception = True
    search_type = SIMPLE_SEARCH

    filterset_class = LearningUnitFilter
    permission_required = 'base.can_access_learningunit'
    cache_exclude_params = 'xls_status'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        starting_ac = starting_academic_year()

        context.update({
            'form': context['filter'].form,
            'learning_units_count': context["paginator"].count,
            'current_academic_year': starting_ac,
            'proposal_academic_year': starting_ac.next(),
            'search_type': self.search_type,
            'page_obj': context["page_obj"],
            'items_per_page': context["paginator"].per_page,
            "form_comparison": SelectComparisonYears(
                academic_year=get_academic_year_of_reference(context['object_list'])
            ),
        })
        return context

    def get_paginate_by(self, queryset):
        return self.request.GET.get("paginator_size", ITEMS_PER_PAGES)

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            serializer = LearningUnitSerializer(context["page_obj"], context={'request': self.request}, many=True)
            return JsonResponse({'object_list': serializer.data})
        return super().render_to_response(context, **response_kwargs)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
@cache_filter()
def learning_units(request):
    search_type = SIMPLE_SEARCH
    found_learning_units = LearningUnitYear.objects.none()
    learning_unit_filter = LearningUnitFilter(request.GET or None)
    form = learning_unit_filter.form
    if learning_unit_filter.is_valid():
        found_learning_units = learning_unit_filter.qs

    # TODO move xls to decorators
    if request.POST.get('xls_status') == "xls":
        return create_xls(request.user, found_learning_units, _get_filter(form, search_type))

    if request.POST.get('xls_status') == "xls_comparison":
        return create_xls_comparison(
            request.user,
            found_learning_units,
            _get_filter(form, search_type),
            request.POST.get('comparison_year')
        )
    if request.POST.get('xls_status') == "xls_with_parameters":
        return create_xls_with_parameters(
            request.user,
            found_learning_units,
            _get_filter(learning_unit_filter.form, search_type),
            {
                WITH_GRP: request.POST.get('with_grp') == 'true',
                WITH_ATTRIBUTIONS: request.POST.get('with_attributions') == 'true'
            }
        )

    if request.POST.get('xls_status') == "xls_attributions":
        return create_xls_attributions(request.user, found_learning_units, _get_filter(form, search_type))

    items_per_page = request.GET.get("paginator_size", ITEMS_PER_PAGES)
    object_list_paginated = paginate_queryset(found_learning_units, request.GET, items_per_page=items_per_page)
    # TODO move to decorator
    if request.is_ajax():
        serializer = LearningUnitSerializer(object_list_paginated, context={'request': request}, many=True)
        return JsonResponse({'object_list': serializer.data})

    form_comparison = SelectComparisonYears(academic_year=get_academic_year_of_reference(found_learning_units))
    starting_ac = starting_academic_year()

    return render(request, "learning_unit/search/simple.html", {
        'form': form,
        'learning_units_count': len(found_learning_units)
        if isinstance(found_learning_units, list) else
        found_learning_units.count(),
        'current_academic_year': starting_ac,
        'proposal_academic_year': starting_ac.next(),
        'search_type': search_type,
        'page_obj': object_list_paginated,
        'items_per_page': items_per_page,
        "form_comparison": form_comparison,
    })
