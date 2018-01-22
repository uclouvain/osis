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
import datetime

from django.db import transaction

from base.models.enums import academic_calendar_type
from base.models.session_exam_calendar import SessionExamCalendar
from base.models.session_exam_deadline import SessionExamDeadline


def compute_deadline_by_offer_year_calendar(oyc):
    if oyc.academic_calendar.reference != academic_calendar_type.DELIBERATION:
        return

    end_date_offer_year = _one_day_before(oyc.end_date.date()) if oyc.end_date else None
    end_date_academic = oyc.academic_calendar.end_date

    list_sessions = SessionExamCalendar.objects.filter(academic_calendar=oyc.academic_calendar).values('number_session')
    sessions_exam_deadlines = SessionExamDeadline.objects.filter(offer_enrollment__offer_year=oyc.offer_year,
                                                                 number_session__in=list_sessions)

    with transaction.atomic():
        for session in sessions_exam_deadlines:
            deadline = session.deadline
            end_date_student = _one_day_before(session.deliberation_date) if session.deliberation_date else None

            new_deadline = min(filter(None, (end_date_academic, end_date_offer_year, end_date_student)))
            if new_deadline == deadline:
                continue

            session.deadline = new_deadline
            session.save()


def _one_day_before(current_date):
    return current_date - datetime.timedelta(days=1)
