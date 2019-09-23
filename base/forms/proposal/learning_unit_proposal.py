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
from django import forms
from django.db.models import Q, OuterRef, Subquery
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from django_filters import FilterSet, filters, OrderingFilter

from base import models as mdl
from base.business.entity import get_entities_ids
from base.business.learning_unit_year_with_context import append_latest_entities
from base.forms.learning_unit.search_form import LearningUnitSearchForm
from base.models.academic_year import AcademicYear, starting_academic_year
from base.models.entity import Entity
from base.models.entity_version import EntityVersion
from base.models.enums.proposal_state import ProposalState, LimitedProposalState
from base.models.enums.proposal_type import ProposalType
from base.models.learning_unit_year import LearningUnitYear, LearningUnitYearQuerySet
from base.models.proposal_learning_unit import ProposalLearningUnit


def _get_sorted_choices(tuple_of_choices):
    return tuple(sorted(tuple_of_choices, key=lambda item: item[1]))


class ProposalLearningUnitFilter(FilterSet):
    academic_year = filters.ModelChoiceFilter(
        queryset=AcademicYear.objects.all(),
        required=False,
        label=_('Ac yr.'),
        empty_label=pgettext_lazy("plural", "All"),
    )
    acronym = filters.CharFilter(
        field_name="acronym",
        lookup_expr="icontains",
        max_length=40,
        required=False,
        label=_('Code'),
    )
    requirement_entity = filters.CharFilter(
        method='filter_entity',
        max_length=20,
        label=_('Req. Entity'),
    )
    with_entity_subordinated = filters.BooleanFilter(
        method=lambda queryset, *args, **kwargs: queryset,
        label=_('Include subordinate entities'),
        widget=forms.CheckboxInput
    )
    tutor = filters.CharFilter(
        method="filter_tutor",
        max_length=40,
        label=_('Tutor'),
    )
    entity_folder = filters.ChoiceFilter(
        field_name="proposallearningunit__entity_id",
        label=_('Folder entity'),
        required=False,
        empty_label=pgettext_lazy("plural", "All"),
    )
    folder = filters.NumberFilter(
        field_name="proposallearningunit__folder_id",
        min_value=0,
        required=False,
        label=_('Folder num.'),
        widget=forms.TextInput()
    )
    proposal_type = filters.ChoiceFilter(
        field_name="proposallearningunit__type",
        label=_('Proposal type'),
        choices=_get_sorted_choices(ProposalType.choices()),
        required=False,
        empty_label=pgettext_lazy("plural", "All"),
    )
    proposal_state = filters.ChoiceFilter(
        field_name="proposallearningunit__state",
        label=_('Proposal status'),
        choices=_get_sorted_choices(ProposalState.choices()),
        required=False,
        empty_label=pgettext_lazy("plural", "All"),
    )

    order_by_field = 'ordering'
    ordering = OrderingFilter(
        fields=(
            ('academic_year__year', 'academic_year'),
            ('acronym', 'acronym'),
            ('subtype', 'subtype'),
            ('entity_requirement', 'requirement_entity'),
            ('credits', 'credits'),
            ('status', 'status'),
        ),
        widget=forms.HiddenInput
    )

    class Meta:
        model = LearningUnitYear
        fields = [
            "academic_year",
            "acronym",
            "subtype",
            "requirement_entity",
        ]

    def __init__(self, *args, person=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.person = person
        self.queryset = self.get_queryset()
        self.form.fields["academic_year"].initial = starting_academic_year()
        self._get_entity_folder_id_linked_ordered_by_acronym(self.person)

    def _get_entity_folder_id_linked_ordered_by_acronym(self, person):
        entities = Entity.objects.filter(proposallearningunit__isnull=False).distinct()
        entities_sorted_by_acronym = sorted(list(entities.filter(id__in=person.linked_entities)),
                                            key=lambda t: t.most_recent_acronym)
        self.form.fields['entity_folder'].choices = [(ent.pk, ent.most_recent_acronym)
                                                     for ent in entities_sorted_by_acronym]

    def filter_entity(self, queryset, name, value):
        with_subordinated = self.form.cleaned_data['with_entity_subordinated']
        lookup_expression = "__".join(["learning_container_year", name, "in"])
        if value:
            entity_ids = get_entities_ids(value, with_subordinated)
            queryset = queryset.filter(**{lookup_expression: entity_ids})
        return queryset

    def filter_tutor(self, queryset, name, value):
        for tutor_name in value.split():
            queryset = queryset.filter(
                Q(learningcomponentyear__attributionchargenew__attribution__tutor__person__first_name__iregex=
                  tutor_name) |
                Q(learningcomponentyear__attributionchargenew__attribution__tutor__person__last_name__iregex=tutor_name)
            ).distinct()
        return queryset

    def get_queryset(self):
        entity_requirement = EntityVersion.objects.filter(
            entity=OuterRef('learning_container_year__requirement_entity'),
        ).current(
            OuterRef('academic_year__start_date')
        ).values('acronym')[:1]

        queryset = LearningUnitYear.objects_with_container.filter(
            proposallearningunit__isnull=False
        ).select_related(
            'academic_year', 'learning_container_year__academic_year',
            'language', 'proposallearningunit', 'externallearningunityear'
        ).order_by('academic_year__year', 'acronym').annotate(
            entity_requirement=Subquery(entity_requirement),
        )
        queryset = LearningUnitYearQuerySet.annotate_full_title_class_method(queryset)
        return queryset


class ProposalStateModelForm(forms.ModelForm):
    class Meta:
        model = ProposalLearningUnit
        fields = ['state']

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        if kwargs.pop('is_faculty_manager', False):
            self.fields['state'].choices = LimitedProposalState.choices()
