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
from importlib import import_module

from django.conf import settings
from django.conf.urls import url, include

from webservices.api.views.auth_token import AuthToken
from webservices.views import ws_catalog_offer, ws_catalog_common_offer, ws_catalog_common_admission_condition

url_api_v1 = [url(r'^auth/token$', AuthToken.as_view(), name=AuthToken.name)]

webservice_apps = [
    'education_group',
    'reference',
    'continuing_education',
    'base',
    'partnership',
]

for app_name in webservice_apps:
    if app_name in settings.INSTALLED_APPS:
        context = {'app_name': app_name}
        imported_urls = import_module("{app_name}.api.url_v1".format(**context))
        regex = r'^{app_name}/'.format(**context)
        namespace = '{app_name}_api_v1'.format(**context)

        url_api_v1.append(url(regex, include(imported_urls.urlpatterns, namespace=namespace)))

urlpatterns = [
    url('^v0.1/catalog/offer/(?P<year>[0-9]{4})/(?P<language>[a-zA-Z]{2})/common$',
        ws_catalog_common_offer,
        name='v0.1-ws_catalog_common_offer'),
    url('^v0.1/catalog/offer/(?P<year>[0-9]{4})/(?P<language>[a-zA-Z]{2})/common/admission_condition$',
        ws_catalog_common_admission_condition,
        name='v0.1-ws_catalog_common_admission_condition'),
    url('^v0.1/catalog/offer/(?P<year>[0-9]{4})/(?P<language>[a-zA-Z]{2})/(?P<acronym>[a-zA-Z0-9]+)$',
        ws_catalog_offer,
        name='v0.1-ws_catalog_offer'),
    url(r'^v1/', include(url_api_v1)),
]
