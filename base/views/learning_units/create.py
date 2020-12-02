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
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods
from waffle.decorators import waffle_flag

from base.forms.learning_unit.learning_unit_postponement import LearningUnitPostponementForm
from base.models import proposal_learning_unit
from base.models.academic_year import AcademicYear
from base.models.learning_unit_year import LearningUnitYear, find_latest_by_learning_unit
from base.models.person import Person
from base.views.common import show_error_message_for_form_invalid, display_error_messages
from base.views.learning_units.common import show_success_learning_unit_year_creation_message
from education_group.templatetags.academic_year_display import display_as_academic_year
from learning_unit.views.utils import learning_unit_year_getter
from osis_role.contrib.views import permission_required


@login_required
@waffle_flag("learning_unit_create")
@permission_required('base.can_create_learningunit', raise_exception=True)
def create_learning_unit(request, academic_year_id):
    person = get_object_or_404(Person, user=request.user)
    if request.POST.get('academic_year'):
        academic_year_id = request.POST.get('academic_year')

    academic_year = get_object_or_404(AcademicYear, pk=academic_year_id)
    postponement_form = LearningUnitPostponementForm(
        person=person,
        start_postponement=academic_year,
        data=request.POST or None
    )
    if request.method == 'POST':
        if postponement_form.is_valid():
            return _save_and_redirect(postponement_form, request)
        else:
            show_error_message_for_form_invalid(request)

    return render(request, "learning_unit/simple/creation.html", postponement_form.get_context())


@login_required
@waffle_flag("learning_unit_create")
@permission_required('base.can_create_partim', raise_exception=True, fn=learning_unit_year_getter)
@require_http_methods(["POST", "GET"])
def create_partim_form(request, learning_unit_year_id):
    person = get_object_or_404(Person, user=request.user)
    learning_unit_year_full = get_object_or_404(LearningUnitYear, pk=learning_unit_year_id)

    if proposal_learning_unit.is_in_creation_proposal(learning_unit_year_full):
        display_error_messages(request, _('You cannot create a partim for a learning unit in proposition of creation'))
        return redirect('learning_unit', learning_unit_year_id=learning_unit_year_id)

    end_postponement = find_latest_by_learning_unit(learning_unit_year_full.learning_unit)

    postponement_form = LearningUnitPostponementForm(
        person=person,
        learning_unit_full_instance=learning_unit_year_full.learning_unit,
        start_postponement=learning_unit_year_full.academic_year,
        end_postponement=end_postponement.academic_year,
        data=request.POST or None,
        external=learning_unit_year_full.is_external()
    )

    if postponement_form.is_valid():
        return _save_and_redirect(postponement_form, request)
    else:
        _manage_future_specific_title_error(learning_unit_year_full, postponement_form, request)

    context = postponement_form.get_context()
    context.update({'learning_unit_year': learning_unit_year_full, 'partim_creation': True})

    return render(request, "learning_unit/simple/creation_partim.html", context)


def _manage_future_specific_title_error(learning_unit_year_full, postponement_form, request):
    for i in range(1, len(postponement_form.errors)):
        if postponement_form.errors[i] and "specific_title" in postponement_form.errors[i][0]:
            msg = _(
                "The learning unit %(code)s doesn't have any Title - Common part in %(ac)s, "
                "it is then neccessary to specify a Title - Specific complement on the partim."
            ) % {
                "code": learning_unit_year_full.acronym,
                "ac": display_as_academic_year(postponement_form.start_postponement.year + i)
            }
            display_error_messages(request, msg)


def _save_and_redirect(postponement_form, request):
    new_luys = postponement_form.save()
    for luy in new_luys:
        show_success_learning_unit_year_creation_message(request, luy)
    return redirect('learning_unit', learning_unit_year_id=new_luys[0].pk)
