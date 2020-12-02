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
from django.db import models

from attribution.models.enums.function import Functions
from osis_common.models.serializable_model import SerializableModelAdmin, SerializableModel


class AttributionAdmin(SerializableModelAdmin):
    list_display = ('tutor', 'function', 'score_responsible', 'summary_responsible', 'learning_unit_year', 'start_year',
                    'end_year', 'changed')
    list_filter = ('learning_unit_year__academic_year', 'function', 'score_responsible', 'summary_responsible')
    fieldsets = ((None, {'fields': ('learning_unit_year', 'tutor', 'function', 'score_responsible',
                                    'summary_responsible', 'start_year', 'end_year')}),)
    raw_id_fields = ('learning_unit_year', 'tutor')
    search_fields = ['tutor__person__first_name', 'tutor__person__last_name', 'learning_unit_year__acronym',
                     'tutor__person__global_id']


class Attribution(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    start_date = models.DateField(auto_now=False, blank=True, null=True, auto_now_add=False)
    end_date = models.DateField(auto_now=False, blank=True, null=True, auto_now_add=False)
    start_year = models.IntegerField(blank=True, null=True)
    end_year = models.IntegerField(blank=True, null=True)
    function = models.CharField(max_length=35, blank=True, null=True, choices=Functions.choices(), db_index=True)
    learning_unit_year = models.ForeignKey('base.LearningUnitYear', on_delete=models.CASCADE)
    tutor = models.ForeignKey('base.Tutor', on_delete=models.CASCADE)
    score_responsible = models.BooleanField(default=False)
    summary_responsible = models.BooleanField(default=False)

    def __str__(self):
        return u"%s - %s" % (self.tutor.person, self.get_function_display())

    @property
    def duration(self):
        if self.start_year and self.end_year:
            return (self.end_year - self.start_year) + 1
        return None


def search(tutor=None, learning_unit_year=None, score_responsible=None, summary_responsible=None,
           list_learning_unit_year=None):
    queryset = Attribution.objects
    if tutor:
        queryset = queryset.filter(tutor=tutor)
    if learning_unit_year:
        queryset = queryset.filter(learning_unit_year=learning_unit_year)
    if score_responsible is not None:
        queryset = queryset.filter(score_responsible=score_responsible)
    if summary_responsible is not None:
        queryset = queryset.filter(summary_responsible=summary_responsible)
    if list_learning_unit_year is not None:
        queryset = queryset.filter(learning_unit_year__in=list_learning_unit_year)
    return queryset.select_related('tutor__person', 'learning_unit_year')


def find_all_responsibles_by_learning_unit_year(a_learning_unit_year):
    attribution_list = Attribution.objects.filter(learning_unit_year=a_learning_unit_year,
                                                  score_responsible=True) \
        .distinct("tutor") \
        .select_related("tutor")
    return [attribution.tutor for attribution in attribution_list]


def find_responsible(a_learning_unit_year):
    tutors_list = find_all_responsibles_by_learning_unit_year(a_learning_unit_year)
    if tutors_list:
        return tutors_list[0]
    return None


def is_score_responsible(user, learning_unit_year):
    return Attribution.objects.filter(learning_unit_year=learning_unit_year,
                                      score_responsible=True,
                                      tutor__person__user=user)\
                              .count() > 0


def find_all_responsible_by_learning_unit_year(learning_unit_year, responsibles_order=None):
    if not responsibles_order:
        # FIXME :: this code fixes wrong database model. The flags summary_responsible and score_responsible should be
        # FIXME :: in another model than Attribution (to avoid ducplicates tutor name)
        raise AttributeError("Please set the responsibles_order param. It's used to order by attributions from"
                             "scores responsibles or summary responsibles.")
    all_tutors_qs = Attribution.objects.filter(learning_unit_year=learning_unit_year).order_by('tutor')
    if responsibles_order:
        all_tutors_qs = all_tutors_qs.order_by('tutor', responsibles_order)
    all_tutors_qs = all_tutors_qs.distinct('tutor').values_list('id', flat=True)
    return Attribution.objects.filter(id__in=all_tutors_qs).prefetch_related('tutor') \
        .order_by("tutor__person")


def find_by_tutor(tutor):
    if tutor:
        return [att.learning_unit_year for att in list(search(tutor=tutor))]
    else:
        return None


def clear_scores_responsible_by_learning_unit_year(learning_unit_year_pk):
    attributions = Attribution.objects.filter(learning_unit_year__id=learning_unit_year_pk)
    for attribution in attributions:
        setattr(attribution, 'score_responsible', False)
        attribution.save()


def _clear_attributions_field_of_learning__unit_year(learning_unit_year_pk, field_to_clear):
    attributions = Attribution.objects.filter(learning_unit_year__id=learning_unit_year_pk)
    for attribution in attributions:
        setattr(attribution, field_to_clear, False)
        attribution.save()
