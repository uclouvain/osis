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

from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin

from base.models import academic_year
from base.models.academic_year import AcademicYear, MAX_ACADEMIC_YEAR_FACULTY, MAX_ACADEMIC_YEAR_CENTRAL


class AcademicYearAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = AcademicYear.objects.all()

        if self.q:
            qs = qs.filter(year__icontains=self.q)

        return qs.distinct().order_by('year')


class AcademicYearAutocompleteLimited(AcademicYearAutocomplete):
    def get_queryset(self):
        starting_academic_year = academic_year.starting_academic_year()
        end_year_range = MAX_ACADEMIC_YEAR_FACULTY if self.request.user.person.is_faculty_manager \
            else MAX_ACADEMIC_YEAR_CENTRAL
        qs = super(AcademicYearAutocompleteLimited, self).get_queryset().min_max_years(
            starting_academic_year.year, starting_academic_year.year + end_year_range
        )
        return qs
