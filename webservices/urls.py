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
from django.conf.urls import url, include

import continuing_education.api.url_v1
import education_group.api.url_v1
import reference.api.url_v1
from webservices.api.views.auth_token import AuthToken
from webservices.views import ws_catalog_offer, ws_catalog_common_offer, ws_catalog_common_admission_condition

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
    url(r'^v1/', include([
        url(r'^auth/token$', AuthToken.as_view(), name=AuthToken.name),
        url(r'^continuing_education/',
            include(continuing_education.api.url_v1.urlpatterns, namespace='continuing_education_api_v1')),
        url(r'^education_group/',
            include(education_group.api.url_v1, namespace='education_group_api_v1')),
        url(r'^reference/',
            include(reference.api.url_v1, namespace='reference_api_v1')),
    ])),
]
