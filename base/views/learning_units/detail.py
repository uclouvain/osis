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
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

from base.models.person import Person
from base.views.learning_units.common import get_learning_unit_identification_context


@login_required
def learning_unit_identification(request, learning_unit_year_id):
    person = get_object_or_404(Person, user=request.user)
    context = get_learning_unit_identification_context(learning_unit_year_id, person)

    learning_unit_year = context['learning_unit_year']

    if learning_unit_year.is_external():
        template = "learning_unit/external/read.html"
        permission = 'base.can_access_externallearningunityear'
    else:
        template = "learning_unit/identification.html"
        permission = 'base.can_access_learningunit'

    if not person.user.has_perm(permission):
        raise PermissionDenied
    return render(request, template, context)
