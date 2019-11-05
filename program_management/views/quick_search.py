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
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django_filters import FilterSet, filters, OrderingFilter
from django_filters.views import FilterView

from base.models.academic_year import AcademicYear
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories
from base.models.learning_unit_year import LearningUnitYear, LearningUnitYearQuerySet
from base.utils.cache import CacheFilterMixin
from base.utils.search import SearchMixin
from base.views.mixins import AjaxTemplateMixin
from education_group.api.serializers.education_group import EducationGroupSerializer
from learning_unit.api.serializers.learning_unit import LearningUnitSerializer


class QuickEducationGroupYearFilter(FilterSet):
    academic_year = filters.ModelChoiceFilter(
        queryset=AcademicYear.objects.all(),
        required=False,
        label=_('Ac yr.'),
        empty_label=pgettext_lazy("plural", "All"),
    )
    acronym = filters.CharFilter(
        field_name="acronym",
        lookup_expr='icontains',
        max_length=40,
        required=False,
        label=_('Acronym/Short title'),
    )
    title = filters.CharFilter(
        field_name="title",
        lookup_expr='icontains',
        max_length=255,
        required=False,
        label=_('Title')
    )

    ordering = OrderingFilter(
        fields=(
            ('acronym', 'acronym'),
            ('title', 'title'),
        ),
        widget=forms.HiddenInput
    )

    class Meta:
        model = EducationGroupYear
        fields = [
            'acronym',
            'title',
            'academic_year'
        ]

    def __init__(self, *args, initial=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = self.get_queryset()
        if initial:
            self.form.fields["academic_year"].initial = initial["academic_year"]

    def get_queryset(self):
        # Need this close so as to return empty query by default when form is unbound
        if not self.data:
            return EducationGroupYear.objects.none()
        queryset = EducationGroupYear.objects.filter(
            education_group_type__category__in=[
                education_group_categories.Categories.GROUP.name,
                education_group_categories.Categories.MINI_TRAINING.name,
            ]
        )
        return queryset


class QuickLearningUnitYearFilter(FilterSet):
    academic_year = filters.ModelChoiceFilter(
        queryset=AcademicYear.objects.all(),
        required=False,
        label=_('Ac yr.'),
        empty_label=pgettext_lazy("plural", "All"),
    )
    acronym = filters.CharFilter(
        field_name="acronym",
        lookup_expr="iregex",
        max_length=40,
        required=False,
        label=_('Code'),
    )
    title = filters.CharFilter(
        field_name="full_title",
        lookup_expr="icontains",
        max_length=40,
        label=_('Title'),
    )

    ordering = OrderingFilter(
        fields=(
            ('academic_year__year', 'academic_year'),
            ('acronym', 'acronym'),
            ('full_title', 'title'),
        ),
        widget=forms.HiddenInput
    )

    class Meta:
        model = LearningUnitYear
        fields = [
            "academic_year",
            "acronym",
            "title",
        ]

    def __init__(self, *args, initial=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = self.get_queryset()
        if initial:
            self.form.fields["academic_year"].initial = initial["academic_year"]

    def get_queryset(self):
        # Need this close so as to return empty query by default when form is unbound
        if not self.data:
            return LearningUnitYear.objects.none()
        queryset = LearningUnitYear.objects_with_container.select_related(
            'academic_year',
        )
        queryset = LearningUnitYearQuerySet.annotate_full_title_class_method(queryset)
        return queryset


class QuickSearchEducationGroupYearView(PermissionRequiredMixin, CacheFilterMixin, AjaxTemplateMixin, FilterView):
    model = EducationGroupYear
    template_name = 'quick_search_egy_inner.html'
    permission_required = ['base.can_access_education_group', 'base.can_access_learningunit']

    filterset_class = QuickEducationGroupYearFilter
    cache_exclude_params = 'page',
    paginate_by = "12"
    ordering = 'academic_year', 'acronym',

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        egy = get_object_or_404(EducationGroupYear, id=self.kwargs['education_group_year_id'])
        kwargs["initial"] = {'academic_year': egy.academic_year_id}
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = context["filter"].form
        context['root_id'] = self.kwargs['root_id']
        context['education_group_year_id'] = self.kwargs['education_group_year_id']
        return context


class QuickSearchEducationGroupYearSerializer(SearchMixin, QuickSearchEducationGroupYearView):
    serializer_class = EducationGroupSerializer


class QuickSearchLearningUnitYearView(PermissionRequiredMixin, CacheFilterMixin, AjaxTemplateMixin, FilterView):
    model = LearningUnitYear
    template_name = 'quick_search_luy_inner.html'
    permission_required = ['base.can_access_education_group', 'base.can_access_learningunit']

    filterset_class = QuickLearningUnitYearFilter
    cache_exclude_params = 'page',
    paginate_by = "12"
    ordering = 'academic_year', 'acronym',

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        egy = get_object_or_404(EducationGroupYear, id=self.kwargs['education_group_year_id'])
        kwargs["initial"] = {'academic_year': egy.academic_year_id}
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = context["filter"].form
        context['root_id'] = self.kwargs['root_id']
        context['education_group_year_id'] = self.kwargs['education_group_year_id']
        return context


class QuickSearchLearningUnitYearSerializer(SearchMixin, QuickSearchLearningUnitYearView):
    serializer_class = LearningUnitSerializer
