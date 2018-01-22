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
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods

from base.forms.academic_calendar import AcademicCalendarForm
from base.models.enums import academic_calendar_type
from base import models as mdl
from . import layout


def _build_gantt_json(academic_calendar_list):
    today = datetime.date.today()
    academic_calendar_data = []
    for calendar in academic_calendar_list:
        if calendar.start_date is None or calendar.end_date is None:
            continue
        if today <= calendar.start_date:
            progress = 0
        elif calendar.start_date < today < calendar.end_date:
            progress = (today - calendar.start_date) / (calendar.end_date - calendar.start_date)
        else:
            progress = 1

        data = {
            'id': calendar.pk,
            'text': calendar.title,
            'start_date': calendar.start_date.strftime('%d-%m-%Y'),
            'end_date': calendar.end_date.strftime('%d-%m-%Y'),
            'color': academic_calendar_type.ACADEMIC_CALENDAR_TYPES_COLORS.get(calendar.reference, '#337ab7'),
            'progress': progress
        }
        academic_calendar_data.append(data)
    return {
        "data": academic_calendar_data
    }


def _get_undated_calendars(academic_calendar_list):
    undated_calendars_list = []
    for calendar in academic_calendar_list:
        if calendar.start_date is None or calendar.end_date is None:
            undated_calendars_list.append(calendar)
    return undated_calendars_list


@login_required
@permission_required('base.can_access_academic_calendar', raise_exception=True)
def academic_calendars(request):
    academic_year = None
    academic_years = mdl.academic_year.find_academic_years()
    academic_year_calendar = mdl.academic_year.current_academic_year()

    if academic_year_calendar:
        academic_year = academic_year_calendar.id

    academic_calendar_list = mdl.academic_calendar.find_academic_calendar_by_academic_year(academic_year)
    academic_calendar_json = _build_gantt_json(academic_calendar_list)
    undated_calendars_list = _get_undated_calendars(academic_calendar_list)

    return layout.render(request, "academic_calendars.html", locals())


@login_required
@permission_required('base.can_access_academic_calendar', raise_exception=True)
def academic_calendars_search(request):
    academic_year = request.GET['academic_year']
    academic_years = mdl.academic_year.find_academic_years()

    if academic_year is None:
        academic_year_calendar = mdl.academic_year.current_academic_year()
        if academic_year_calendar:
            academic_year = academic_year_calendar.id

    academic_year = int(academic_year)
    academic_calendar_list = mdl.academic_calendar.find_academic_calendar_by_academic_year(academic_year)
    academic_calendar_json = _build_gantt_json(academic_calendar_list)
    undated_calendars_list = _get_undated_calendars(academic_calendar_list)

    return layout.render(request, "academic_calendars.html", locals())


@login_required
@permission_required('base.can_access_academic_calendar', raise_exception=True)
def academic_calendar_read(request, academic_calendar_id):
    academic_calendar = get_object_or_404(mdl.academic_calendar.AcademicCalendar, pk=academic_calendar_id)
    return layout.render(request, "academic_calendar.html", {'academic_calendar': academic_calendar})


@login_required
@permission_required('base.can_access_academic_calendar', raise_exception=True)
@require_http_methods(['GET'])  # Temporary prevent sumbit modification
def academic_calendar_form(request, academic_calendar_id):
    academic_calendar = mdl.academic_calendar.find_by_id(academic_calendar_id)
    if request.method == 'GET':
        academic_cal_form = AcademicCalendarForm(instance=academic_calendar)
    else:
        academic_cal_form = AcademicCalendarForm(data=request.POST, instance=academic_calendar)

        if academic_cal_form.is_valid():
            academic_cal_form.save()
            return academic_calendar_read(request, academic_cal_form.instance.id)
    return layout.render(request, "academic_calendar_form.html", {'form': academic_cal_form})
