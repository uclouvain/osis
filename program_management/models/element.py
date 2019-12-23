##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class ElementAdmin(VersionAdmin, SerializableModelAdmin):
    list_display = ('education_group_year', 'group_year', 'learning_unit_year', 'learning_class_year')
    search_fields = ('education_group_year__acronym',
                     'group_year__acronym',
                     'learning_unit_year__acronym',
                     'learning_class_year__acronym')


class Element(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)

    education_group_year = models.ForeignKey(
        'base.EducationGroupYear',
        blank=True, null=True,
        verbose_name=_('education group year'),
        on_delete=models.CASCADE
    )
    group_year = models.ForeignKey(
        'education_group.GroupYear',
        blank=True, null=True,
        verbose_name=_('group year'),
        on_delete=models.CASCADE
    )
    learning_unit_year = models.ForeignKey(
        'base.LearningUnitYear',
        blank=True, null=True,
        verbose_name=_('learning unit year'),
        on_delete=models.CASCADE,
    )
    learning_class_year = models.ForeignKey(
        'base.LearningClassYear',
        blank=True, null=True,
        verbose_name=_('learning class year'),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return u"%s - %s - %s - %s" % (
            u"Education group year : %s" % (self.education_group_year) if self.education_group_year else '',
            u"Group year : %s" % (self.group_year) if self.group_year else '',
            u"Learning unit year : %s" % (self.learning_unit_year) if self.learning_unit_year else '',
            u"Learning class year : %s" % (self.learning_class_year) if self.learning_class_year else ''
        )

    def clean(self):
        super().clean()
        if not (
                self.education_group_year or self.group_year
                or self.learning_class_year or self.learning_unit_year):
            raise ValidationError(
                _(
                    'At least an education group year, a group year, a learning unit year or a learning class '
                    'year has to be set')
            )
