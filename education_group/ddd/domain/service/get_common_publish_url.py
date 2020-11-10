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
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from osis_common.ddd import interface


class GetCommonPublishUrl(interface.DomainService):
    @classmethod
    def get_url_admission_conditions(cls, year: int) -> str:
        if not all([settings.ESB_API_URL, settings.ESB_REFRESH_COMMON_ADMISSION_ENDPOINT]):
            raise ImproperlyConfigured('ESB_API_URL / ESB_REFRESH_COMMON_ADMISSION_ENDPOINT'
                                       'must be set in configuration')

        endpoint = settings.ESB_REFRESH_COMMON_ADMISSION_ENDPOINT.format(year=year)
        return "{esb_api}/{endpoint}".format(esb_api=settings.ESB_API_URL, endpoint=endpoint)

    @classmethod
    def get_url_pedagogy(cls, year: int) -> str:
        if not all([settings.ESB_API_URL, settings.ESB_REFRESH_COMMON_PEDAGOGY_ENDPOINT]):
            raise ImproperlyConfigured('ESB_API_URL / ESB_REFRESH_COMMON_PEDAGOGY_ENDPOINT'
                                       'must be set in configuration')

        endpoint = settings.ESB_REFRESH_COMMON_PEDAGOGY_ENDPOINT.format(year=year)
        return "{esb_api}/{endpoint}".format(esb_api=settings.ESB_API_URL, endpoint=endpoint)
