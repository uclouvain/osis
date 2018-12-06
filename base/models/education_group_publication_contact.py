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
##############################################################################
from django.utils.translation import ugettext_lazy as _

from django.db import models
from ordered_model.admin import OrderedModelAdmin
from ordered_model.models import OrderedModel

from base.models.enums.publication_contact_type import PublicationContactType


class EducationGroupPublicationContactAdmin(OrderedModelAdmin):
    list_display = ('education_group_year', 'type', 'role', 'email', 'order', 'move_up_down_links',)
    readonly_fields = ['order']
    search_fields = ['education_group_year__acronym', 'role', 'email']


class EducationGroupPublicationContact(OrderedModel):
    role = models.CharField(max_length=100, default='', blank=True)
    email = models.EmailField(
        verbose_name=_('email'),
    )
    type = models.CharField(
        max_length=100,
        choices=PublicationContactType.choices(),
        default=PublicationContactType.OTHER_CONTACT.name,
        verbose_name=_('type'),
    )
    education_group_year = models.ForeignKey('EducationGroupYear')
    order_with_respect_to = ('education_group_year', 'type', )

    class Meta:
        ordering = ('education_group_year', 'type', 'order',)
