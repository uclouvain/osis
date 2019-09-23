from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render

from base.business.learning_units.xls_comparison import get_academic_year_of_reference
from base.forms.learning_unit.comparison import SelectComparisonYears
from base.forms.learning_unit.search_form import ExternalLearningUnitYearForm, ExternalLearningUnitFilter
from base.models.academic_year import starting_academic_year, get_last_academic_years
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.utils.cache import cache_filter
from base.views.common import check_if_display_message, paginate_queryset
from base.views.learning_units.search.common import _manage_session_variables, EXTERNAL_SEARCH, ITEMS_PER_PAGES


@login_required
@permission_required('base.can_access_externallearningunityear', raise_exception=True)
@cache_filter()
def learning_units_external_search(request):
    _manage_session_variables(request, 'EXTERNAL')

    starting_ac_year = starting_academic_year()
    search_form = ExternalLearningUnitFilter(request.GET or None)
    user_person = get_object_or_404(Person, user=request.user)
    found_learning_units = LearningUnitYear.objects.none()

    if search_form.is_valid():
        found_learning_units = search_form.qs
        check_if_display_message(request, found_learning_units)

    context = {
        'form': search_form.form,
        'academic_years': get_last_academic_years(),
        'current_academic_year': starting_ac_year,
        'search_type': EXTERNAL_SEARCH,
        'learning_units_count': found_learning_units.count(),
        'is_faculty_manager': user_person.is_faculty_manager,
        'form_comparison': SelectComparisonYears(academic_year=get_academic_year_of_reference(found_learning_units)),
        'page_obj': paginate_queryset(found_learning_units, request.GET, items_per_page=ITEMS_PER_PAGES),
    }
    return render(request, "learning_unit/search/external.html", context)
