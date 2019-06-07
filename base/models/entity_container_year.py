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
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _
from reversion.admin import VersionAdmin

from base.models import entity_version
from base.models.enums.entity_container_year_link_type import EntityContainerYearLinkTypes
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class EntityContainerYearAdmin(VersionAdmin, SerializableModelAdmin):
    list_display = ('external_id', 'learning_container_year', 'entity', 'type')
    search_fields = ['learning_container_year__acronym', 'type']
    list_filter = ('learning_container_year__academic_year',)


class EntityContainerYear(SerializableModel):
    external_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    entity = models.ForeignKey('Entity', on_delete=models.CASCADE)
    learning_container_year = models.ForeignKey('LearningContainerYear', on_delete=models.CASCADE)
    type = models.CharField(max_length=35, choices=EntityContainerYearLinkTypes.choices())
    _warnings = None

    class Meta:
        unique_together = ('learning_container_year', 'type',)

    def __str__(self):
        return u"%s - %s - %s" % (self.entity, self.learning_container_year, self.type)

    def get_latest_entity_version(self):
        # Sometimes, entity-versions is prefetch to optimized queries
        if getattr(self.entity, "entity_versions", None):
            return self.entity.entity_versions[-1]
        return self.entity.entityversion_set.order_by('start_date').last()

    # @property
    # def warnings(self):
    #     if self._warnings is None:
    #         self._warnings = []
    #         if not entity_version.get_by_entity_and_date(self.entity,
    #                                                      self.learning_container_year.academic_year.start_date):
    #             self._warnings.append(_("The linked %(entity)s does not exist at the start date of the academic year"
    #                                     " linked to this learning unit") % {'entity': self.get_type_display().lower()})
    #     return self._warnings
