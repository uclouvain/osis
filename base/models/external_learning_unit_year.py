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

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from base.models.learning_unit_year import MINIMUM_CREDITS, MAXIMUM_CREDITS
from osis_common.models.osis_model_admin import OsisModelAdmin


class ExternalLearningUnitYearAdmin(VersionAdmin, OsisModelAdmin):
    list_display = ('external_id', 'external_acronym', 'external_credits', 'url', 'learning_unit_year',
                    'requesting_entity', "author", "creation_date")
    search_fields = ['learning_unit_year__acronym']


class ExternalLearningUnitYear(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)

    external_acronym = models.CharField(
        null=True,
        blank=True,
        max_length=25,
        db_index=True,
        verbose_name=_('External code')
    )

    external_credits = models.DecimalField(
        null=True,
        blank=True,
        max_digits=5,
        decimal_places=2,
        verbose_name=_('Local credits'),
        validators=[
            MinValueValidator(MINIMUM_CREDITS),
            MaxValueValidator(MAXIMUM_CREDITS)
        ]
    )

    url = models.URLField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('URL of the learning unit'),
    )

    learning_unit_year = models.OneToOneField(
        'LearningUnitYear',
        on_delete=models.CASCADE,
        verbose_name=_('learning unit year'),
    )

    requesting_entity = models.ForeignKey(
        'Entity',
        null=True,
        blank=True,
        verbose_name=_('Requesting entity'),
        on_delete=models.PROTECT,
    )

    co_graduation = models.BooleanField(default=False, verbose_name=_('Co-graduation'))
    mobility = models.BooleanField(default=False, verbose_name=_('Mobility'))
    author = models.ForeignKey('Person', null=True, on_delete=models.PROTECT)
    creation_date = models.DateTimeField(null=True, auto_now_add=True)

    class Meta:
        unique_together = ('learning_unit_year', 'external_acronym',)

        permissions = (
            ("can_access_externallearningunityear", "Can access external learning unit year"),
        )

    def __str__(self):
        return u"%s" % self.external_acronym
