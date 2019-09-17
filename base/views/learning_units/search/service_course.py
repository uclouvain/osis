from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render

from base.business.learning_unit_xls import create_xls, create_xls_with_parameters, WITH_GRP, WITH_ATTRIBUTIONS, \
    create_xls_attributions
from base.business.learning_units.xls_comparison import create_xls_comparison, get_academic_year_of_reference
from base.forms.learning_unit.comparison import SelectComparisonYears
from base.forms.learning_unit.search_form import LearningUnitYearForm, LearningUnitFilter
from base.models.academic_year import starting_academic_year
from base.models.learning_unit_year import LearningUnitYear
from base.utils.cache import cache_filter
from base.views.common import paginate_queryset
from base.views.learning_units.search.common import SERVICE_COURSES_SEARCH, _manage_session_variables, _get_filter, \
    ITEMS_PER_PAGES
from learning_unit.api.serializers.learning_unit import LearningUnitSerializer


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
@cache_filter()
def learning_units_service_course(request):
    # TODO adapt filter to service course
    search_type = SERVICE_COURSES_SEARCH
    _manage_session_variables(request, search_type)

    form = LearningUnitYearForm(
        request.GET or None,
        initial={'academic_year_id': starting_academic_year(), 'with_entity_subordinated': True}
    )

    found_learning_units = LearningUnitYear.objects.none()
    form_filter = LearningUnitFilter(request.GET or None)
    if form_filter.is_valid():
        found_learning_units = form_filter.qs

    # TODO move xls to other views
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
            _get_filter(form, search_type),
            {
                WITH_GRP: request.POST.get('with_grp') == 'true',
                WITH_ATTRIBUTIONS: request.POST.get('with_attributions') == 'true'
            }
        )

    if request.POST.get('xls_status') == "xls_attributions":
        return create_xls_attributions(request.user, found_learning_units, _get_filter(form, search_type))

    items_per_page = request.GET.get("paginator_size", ITEMS_PER_PAGES)
    object_list_paginated = paginate_queryset(found_learning_units, request.GET, items_per_page=items_per_page)
    if request.is_ajax():
        serializer = LearningUnitSerializer(object_list_paginated, context={'request': request}, many=True)
        return JsonResponse({'object_list': serializer.data})
    form_comparison = SelectComparisonYears(academic_year=get_academic_year_of_reference(found_learning_units))
    starting_ac = starting_academic_year()
    context = {
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
    }

    return render(request, "learning_unit/search/simple.html", context)