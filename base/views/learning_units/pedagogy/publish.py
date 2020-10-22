############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.models.learning_unit_year import LearningUnitYear
from base.views.common import display_error_messages


@login_required
def publish_and_access_publication(request, code: str, year: int):
    try:
        __publish_pedagogy(code, year)
        redirect_url = settings.LEARNING_UNIT_PORTAL_URL.format(code=code, year=year)
    except LearningUnitPedagogyPublishException:
        error_msg = _("Unable to publish pedagogy information for the learning unit %(code)s - %(year)s") % {
            'code': code,
            'year': year
        }
        display_error_messages(request, error_msg)
        redirect_url = reverse(
            'view_educational_information',
            kwargs={'learning_unit_year_id': LearningUnitYear.objects.get(acronym=code, academic_year__year=year).pk}
        )
    return HttpResponseRedirect(redirect_url)


def __publish_pedagogy(code: str, year: int):
    publish_endpoint = settings.ESB_REFRESH_LEARNING_UNIT_PEDAGOGY_ENDPOINT.format(code=code, year=year)
    try:
        response = requests.get(
            "{esb_api}/{endpoint}".format(esb_api=settings.ESB_API_URL, endpoint=publish_endpoint),
            headers={"Authorization": settings.ESB_AUTHORIZATION},
            timeout=settings.REQUESTS_TIMEOUT
        )
        if response.status_code != HttpResponse.status_code:
            raise LearningUnitPedagogyPublishException()
        return True
    except Exception:
        raise LearningUnitPedagogyPublishException()


class LearningUnitPedagogyPublishException(Exception):
    pass
