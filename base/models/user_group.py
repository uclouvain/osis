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

from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


# class StudentAdmin(SerializableModelAdmin):
#     list_display = ('person', 'registration_id', 'changed',)
#     list_filter = ('person__gender', 'person__language',)
#     search_fields = ['person__first_name', 'person__last_name', 'registration_id']


class UserGroup(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    group = models.ForeignKey('auth.Group', on_delete=models.PROTECT)

    def __str__(self):
        return u"%s (%s)" % (self.user, self.group)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'

