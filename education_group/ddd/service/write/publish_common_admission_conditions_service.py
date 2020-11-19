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
import requests
from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from education_group.ddd.command import PublishCommonAdmissionCommand
from education_group.ddd.domain.service.get_common_publish_url import GetCommonPublishUrl


@transaction.atomic()
def publish_common_admission_conditions(cmd: PublishCommonAdmissionCommand) -> None:
    publish_url = GetCommonPublishUrl.get_url_admission_conditions(cmd.year)
    try:
        requests.get(
            publish_url,
            headers={"Authorization": settings.ESB_AUTHORIZATION},
            timeout=settings.REQUESTS_TIMEOUT or 20
        )
    except Exception:
        raise PublishCommonAdmissionConditionException(year=cmd.year)


class PublishCommonAdmissionConditionException(Exception):
    def __init__(self, year: int, **kwargs):
        self.message = _("Unable to publish common admission conditions for {year}").format(year=year)
        super().__init__(**kwargs)
