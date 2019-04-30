# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from django import forms
from django.db.models import Q
from django.views.generic import ListView

from base.models.academic_year import current_academic_year, AcademicYear
from base.models.learning_unit_year import LearningUnitYear
from base.utils.cache import CacheFilterMixin
from base.views.mixins import AjaxTemplateMixin


class QuickSearchForm(forms.Form):
    academic_year = forms.ModelChoiceField(AcademicYear.objects.all(), required=True)
    search_text = forms.CharField(required=False)


class QuickSearchView(CacheFilterMixin, AjaxTemplateMixin, ListView):
    model = LearningUnitYear
    paginate_by = "12"
    ordering = 'academic_year', 'acronym',
    template_name = 'base/learningunityear_filter_inner.html'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.GET.get('academic_year'):
            qs = qs.filter(academic_year=self.request.GET['academic_year'])

        search_text = self.request.GET.get('search_text')
        if search_text:
            qs = qs.filter(Q(acronym__icontains=search_text) | Q(specific_title__icontains=search_text))

        return qs.select_related('academic_year', 'learning_container_year')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = QuickSearchForm(
            initial={
                'academic_year': self.request.GET.get('academic_year', current_academic_year()),
                'search_text': self.request.GET.get('search_text', ''),
            }
        )
        return context
