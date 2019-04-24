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
import datetime

from django.db.models import Q
from notifications.signals import notify

from base.models.academic_calendar import AcademicCalendar
from base.utils.notifications import get_notifications_last_time_read_for_user, \
    set_notifications_last_read_as_now_for_user, apply_function_if_data_not_in_cache

ALERT_WEEK = 2


class NotificationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            send_academic_calendar_notifications(request.user)

        response = self.get_response(request)
        return response


@apply_function_if_data_not_in_cache
def send_academic_calendar_notifications(user):
    time_last_read = get_notifications_last_time_read_for_user(user)
    ac_qs = AcademicCalendar.objects.starting_within(weeks=ALERT_WEEK).order_by("start_date", "end_date")

    if time_last_read:
        ac_qs = ac_qs.filter(Q(start_date__gt=time_last_read+datetime.timedelta(weeks=ALERT_WEEK))
                             | Q(changed__gt=time_last_read))

    for ac_obj in ac_qs:
        verb = "{} ({})".format(ac_obj.title, ac_obj.start_date.strftime("%d/%m"))
        notify.send(ac_obj, recipient=user, verb=verb)

    set_notifications_last_read_as_now_for_user(user)
