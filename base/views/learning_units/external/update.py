############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext as _

from base.forms.learning_unit.external_learning_unit import ExternalLearningUnitBaseForm
from base.models.person import Person
from base.views.common import display_success_messages


def update_external_learning_unit(request, learning_unit_year):
    person = get_object_or_404(Person, user=request.user)

    external_form = ExternalLearningUnitBaseForm(
        person=person,
        academic_year=learning_unit_year.academic_year,
        learning_unit_instance=learning_unit_year.learning_unit,
        data=request.POST or None
    )

    if external_form.is_valid():
        learning_unit_year = external_form.save()

        display_success_messages(request, _('success_modification_learning_unit'))

        return redirect('learning_unit', learning_unit_year_id=learning_unit_year.pk)

    return render(request, "learning_unit/external/update.html", external_form.get_context())
