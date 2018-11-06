##############################################################################
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
##############################################################################
import functools
import operator

from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import Q

from base.models.person import Person


class EmployeeAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Person.objects.filter(employee=True)

        # FIXME Use trigram search
        if self.q:
            search_queries = functools.reduce(operator.and_,
                                              (SearchQuery(word) for word in self.q.split()))
            qs = qs.annotate(search=SearchVector("first_name", "middle_name", "last_name")) \
                .filter(Q(search=search_queries) | Q(global_id=self.q))

        return qs.order_by("last_name", "first_name")

    def get_result_label(self, result):
        return "{last_name} {first_name} ({age})".format(last_name=result.last_name,
                                                         first_name=result.first_name,
                                                         age=result.age)