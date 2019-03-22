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
from django.db import models
from django.utils.translation import gettext_lazy as _

from osis_common.models.osis_model_admin import OsisModelAdmin


class OrganizationAddressAdmin(OsisModelAdmin):
    list_display = ('organization', 'label', 'location', 'postal_code', 'city', 'country')
    search_fields = ['organization__name', 'label', 'country__name']


class OrganizationAddress(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    organization = models.ForeignKey('Organization')
    # TODO is_main and label are similar.
    # TODO rename label to type
    # FIXME Create a FK directly between Organization and Address for main address.
    label = models.CharField(max_length=20, verbose_name=_("Label"))
    location = models.CharField(max_length=255, verbose_name=_("Location"))
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Postal code"))
    city = models.CharField(max_length=255, verbose_name=_("City"))
    country = models.ForeignKey('reference.Country', verbose_name=_("Country"))
    is_main = models.BooleanField(default=False)


def find_by_organization(organization):
    return OrganizationAddress.objects.filter(organization=organization).order_by('label')


def find_by_id(organization_address_id):
    return OrganizationAddress.objects.get(pk=organization_address_id)


def find_distinct_by_country(a_country):
    return OrganizationAddress.objects.filter(country=a_country).distinct('city').order_by('city').values('city')
