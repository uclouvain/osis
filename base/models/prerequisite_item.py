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
#############################################################################
import itertools

from django.db import models
from django.utils.translation import ugettext_lazy as _

from base.models.enums.prerequisite_operator import OR, AND
from osis_common.models.osis_model_admin import OsisModelAdmin


class PrerequisiteItemAdmin(OsisModelAdmin):
    list_display = ('prerequisite', 'learning_unit', 'group_number', 'position')
    raw_id_fields = ('learning_unit', 'prerequisite')
    list_filter = ('prerequisite__learning_unit_year__academic_year',)
    search_fields = [
        'learning_unit__id',
        'learning_unit__learningunityear__acronym',
        'learning_unit__learningunityear__specific_title',
        'prerequisite__learning_unit_year__acronym',
        'prerequisite__learning_unit_year__specific_title',
        'prerequisite__education_group_year__acronym',
        'prerequisite__education_group_year__title',
    ]


class PrerequisiteItem(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)

    learning_unit = models.ForeignKey("LearningUnit")
    prerequisite = models.ForeignKey("Prerequisite")

    group_number = models.PositiveIntegerField()
    position = models.PositiveIntegerField()

    class Meta:
        unique_together = (
            ('prerequisite', 'group_number', 'position',),
        )


def find_by_prerequisite(prerequisite):
    return PrerequisiteItem.objects.filter(prerequisite=prerequisite)


def find_by_learning_unit_year_having_prerequisite(learning_unit_year):
    return PrerequisiteItem.objects.filter(prerequisite__learning_unit_year=learning_unit_year)


def find_by_learning_unit_being_prerequisite(learning_unit):
    return PrerequisiteItem.objects.filter(learning_unit=learning_unit)


def get_prerequisite_string_representation(prerequisite):
    main_operator = prerequisite.main_operator
    secondary_operator = OR if main_operator == AND else AND
    prerequisite_items = find_by_prerequisite(prerequisite).order_by('group_number', 'position')
    prerequisites_fragments = []

    for num_group, records_in_group in itertools.groupby(prerequisite_items, lambda rec: rec.group_number):
        list_records = list(records_in_group)
        predicate_format = "({})" if len(list_records) > 1 else "{}"
        join_secondary_operator = " {} ".format(_(secondary_operator))
        predicate = predicate_format.format(
            join_secondary_operator.join(
                map(
                    lambda rec: rec.learning_unit.acronym,
                    list_records
                )
            )
        )
        prerequisites_fragments.append(predicate)

    join_main_operator = " {} ".format(_(main_operator))
    return join_main_operator.join(prerequisites_fragments)


def delete_items_by_related_prerequisite(prerequisite):
    PrerequisiteItem.objects.filter(prerequisite=prerequisite).delete()
