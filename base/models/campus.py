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
from django.db import models
from base.models.enums.organization_type import MAIN
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class CampusAdmin(SerializableModelAdmin):
    list_display = ('name', 'organization', 'changed')
    list_filter = ('organization',)
    fieldsets = ((None, {'fields': ('name', 'organization', 'code', 'is_administration')}),)
    search_fields = ['name', 'organization__name']


class Campus(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    organization = models.ForeignKey('Organization')
    code = models.CharField(max_length=1, blank=True, null=True)
    is_administration = models.BooleanField(default=False)

    def __str__(self):
        return u"%s" % self.name


def find_by_organization(organization):
    return Campus.objects.filter(organization=organization)\
                         .order_by('name')


def find_administration_campuses():
    return Campus.objects.filter(organization__type=MAIN, is_administration=True).order_by('name')


def find_by_id(campus_id):
    try:
        return Campus.objects.get(id=campus_id)
    except Campus.DoesNotExist:
        return None
