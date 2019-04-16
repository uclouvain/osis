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
from django.db import models
from osis_common.models import osis_model_admin


class LearningUnitComponentClassAdmin(osis_model_admin.OsisModelAdmin):
    list_display = ('learning_unit_component', 'learning_class_year')
    list_filter = ('learning_unit_component__learning_unit_year__academic_year',)
    search_fields = ['learning_unit_component__learning_unit_year__acronym']


class LearningUnitComponentClass(models.Model):
    learning_unit_component = models.ForeignKey('LearningUnitComponent')
    learning_class_year = models.ForeignKey('LearningClassYear')

    def save(self, *args, **kwargs):
        learning_component_year = self.learning_unit_component.learning_component_year
        if learning_component_year.id != self.learning_class_year.learning_component_year.id:
            raise AttributeError(
                "Learning Component Year is different in Learning Unit Component and Learning Class Year"
            )
        super(LearningUnitComponentClass, self).save(*args, **kwargs)

    class Meta:
        permissions = (
            ("can_access_learningunitcomponentclass", "Can access learning unit component class"),
        )


def find_by_learning_class_year(learning_class_year):
    return LearningUnitComponentClass.objects.filter(learning_class_year=learning_class_year)


def search(learning_unit_component=None, learning_class_year=None):
    queryset = LearningUnitComponentClass.objects

    if isinstance(learning_unit_component, list):
        queryset = queryset.filter(learning_unit_component__in=learning_unit_component)
    elif learning_unit_component:
        queryset = queryset.filter(learning_unit_component=learning_unit_component)

    if learning_class_year:
        queryset = queryset.filter(learning_class_year=learning_class_year)

    return queryset
