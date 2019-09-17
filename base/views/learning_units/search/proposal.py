from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.messages import WARNING
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.business import learning_unit_proposal as proposal_business
from base.business.learning_units.xls_comparison import create_xls_proposal_comparison, get_academic_year_of_reference
from base.business.proposal_xls import create_xls as create_xls_proposal
from base.forms.learning_unit.comparison import SelectComparisonYears
from base.forms.proposal.learning_unit_proposal import LearningUnitProposalForm, ProposalStateModelForm
from base.forms.search.search_form import get_research_criteria
from base.models.academic_year import starting_academic_year, get_last_academic_years
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.models.proposal_learning_unit import ProposalLearningUnit
from base.utils.cache import cache_filter
from base.views.common import check_if_display_message, display_messages_by_level, paginate_queryset
from base.views.learning_units.search.common import _manage_session_variables, PROPOSAL_SEARCH, _get_filter, \
    ITEMS_PER_PAGES, \
    ACTION_BACK_TO_INITIAL, ACTION_CONSOLIDATE, ACTION_FORCE_STATE


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
@cache_filter()
def learning_units_proposal_search(request):
    _manage_session_variables(request, PROPOSAL_SEARCH)

    user_person = get_object_or_404(Person, user=request.user)
    starting_ac_year = starting_academic_year()
    search_form = LearningUnitProposalForm(
        request.GET or None,
        person=user_person,
        initial={'academic_year_id': starting_ac_year, 'with_entity_subordinated': True},
    )
    found_learning_units = LearningUnitYear.objects.none()

    if search_form.is_valid():
        found_learning_units = search_form.get_proposal_learning_units()
        check_if_display_message(request, found_learning_units)

    if request.POST.get('xls_status_proposal') == "xls":
        return create_xls_proposal(
            user_person.user,
            list(found_learning_units),
            _get_filter(search_form, PROPOSAL_SEARCH)
        )

    if request.POST.get('xls_status_proposal') == "xls_comparison":
        return create_xls_proposal_comparison(
            user_person.user,
            list(found_learning_units),
            _get_filter(search_form, PROPOSAL_SEARCH)
        )

    if request.POST:
        research_criteria = get_research_criteria(search_form) if search_form.is_valid() else []

        selected_proposals_id = request.POST.getlist("selected_action", default=[])
        selected_proposals = ProposalLearningUnit.objects.filter(id__in=selected_proposals_id)
        messages_by_level = apply_action_on_proposals(selected_proposals, user_person, request.POST, research_criteria)
        display_messages_by_level(request, messages_by_level)
        return redirect(reverse("learning_unit_proposal_search") + "?{}".format(request.GET.urlencode()))

    context = {
        'form': search_form,
        'form_proposal_state': ProposalStateModelForm(is_faculty_manager=user_person.is_faculty_manager),
        'academic_years': get_last_academic_years(),
        'current_academic_year': starting_ac_year,
        'search_type': PROPOSAL_SEARCH,
        'learning_units_count': found_learning_units.count(),
        'can_change_proposal_state': user_person.is_faculty_manager or user_person.is_central_manager,
        'form_comparison': SelectComparisonYears(academic_year=get_academic_year_of_reference(found_learning_units)),
        'page_obj': paginate_queryset(found_learning_units, request.GET, items_per_page=ITEMS_PER_PAGES),
    }
    return render(request, "learning_unit/search/proposal.html", context)


def apply_action_on_proposals(proposals, author, post_data, research_criteria):
    if not bool(proposals):
        return {WARNING: [_("No proposals was selected.")]}

    action = post_data.get("action", "")
    messages_by_level = {}
    if action == ACTION_BACK_TO_INITIAL:
        messages_by_level = proposal_business.cancel_proposals_and_send_report(proposals, author, research_criteria)
    elif action == ACTION_CONSOLIDATE:
        messages_by_level = proposal_business.consolidate_proposals_and_send_report(proposals, author,
                                                                                    research_criteria)
    elif action == ACTION_FORCE_STATE:
        form = ProposalStateModelForm(post_data)
        if form.is_valid():
            new_state = form.cleaned_data.get("state")
            messages_by_level = proposal_business.force_state_of_proposals(proposals, author, new_state)
    return messages_by_level
