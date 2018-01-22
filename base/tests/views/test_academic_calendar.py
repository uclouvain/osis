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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
from django.test import TestCase, RequestFactory
from unittest import mock
from django.core.urlresolvers import reverse

from base.forms.academic_calendar import AcademicCalendarForm
from base.models.academic_year import AcademicYear
from base.models.enums import academic_calendar_type
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.academic_year import AcademicYearFactory

now = datetime.datetime.now()
today = datetime.date.today()


class AcademicCalendarViewTestCase(TestCase):
    def setUp(self):
        self.academic_year_1 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 1),
                                                         end_date=today.replace(year=today.year + 2),
                                                         year=today.year + 1)
        self.academic_year_2 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 2),
                                                         end_date=today.replace(year=today.year + 3),
                                                         year=today.year + 2)
        self.academic_year_3 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 3),
                                                         end_date=today.replace(year=today.year + 4),
                                                         year=today.year + 3)
        self.academic_year_4 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 4),
                                                         end_date=today.replace(year=today.year + 5),
                                                         year=today.year + 4)
        self.academic_year_5 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 5),
                                                         end_date=today.replace(year=today.year + 6),
                                                         year=today.year + 5)
        self.academic_year_6 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 6),
                                                         end_date=today.replace(year=today.year + 7),
                                                         year=today.year + 6)
        self.current_academic_year = AcademicYearFactory.build(start_date=today,
                                                               end_date=today.replace(year=today.year + 1),
                                                               year=today.year)
        self.current_academic_year.save()
        super(AcademicYear, self.academic_year_1).save()
        super(AcademicYear, self.academic_year_2).save()
        super(AcademicYear, self.academic_year_3).save()
        super(AcademicYear, self.academic_year_4).save()
        super(AcademicYear, self.academic_year_5).save()
        super(AcademicYear, self.academic_year_6).save()

        self.current_academic_calendar = AcademicCalendarFactory.build(academic_year=self.current_academic_year)
        self.current_academic_calendar.save(functions=[])
        self.academic_calendar_1 = AcademicCalendarFactory.build(academic_year=self.academic_year_1)
        self.academic_calendar_1.save(functions=[])
        AcademicCalendarFactory.build(academic_year=self.academic_year_2).save(functions=[])
        AcademicCalendarFactory.build(academic_year=self.academic_year_3).save(functions=[])
        AcademicCalendarFactory.build(academic_year=self.academic_year_4).save(functions=[])
        AcademicCalendarFactory.build(academic_year=self.academic_year_5).save(functions=[])
        AcademicCalendarFactory.build(academic_year=self.academic_year_6).save(functions=[])

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_academic_calendars(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        request_factory = RequestFactory()

        request = request_factory.get(reverse('academic_calendars'))
        request.user = mock.Mock()

        from base.views.academic_calendar import academic_calendars

        academic_calendars(request)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'academic_calendars.html')
        self._compare_academic_calendar_json(context, self.current_academic_calendar)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_academic_calendars_search(self, mock_render, mock_decorators):
        from base.views.academic_calendar import academic_calendars_search

        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        request_factory = RequestFactory()
        get_data = {'academic_year': self.academic_year_1.id}
        request = request_factory.get(reverse('academic_calendars_search'), get_data)
        request.user = mock.Mock()

        academic_calendars_search(request)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'academic_calendars.html')
        self._compare_academic_calendar_json(context, self.academic_calendar_1)

    def _compare_academic_calendar_json(self, context, calendar):
        self.assertDictEqual(
            context['academic_calendar_json'],
            {'data': [
                {'color': academic_calendar_type.ACADEMIC_CALENDAR_TYPES_COLORS.get(calendar.reference, '#337ab7'),
                 'text': calendar.title,
                 'start_date': calendar.start_date.strftime('%d-%m-%Y'),
                 'end_date': calendar.end_date.strftime('%d-%m-%Y'),
                 'progress': 0,
                 'id': calendar.id}]}
        )

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_academic_calendar_read(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        from base.views.academic_calendar import academic_calendar_form

        request_factory = RequestFactory()

        request = request_factory.get(reverse('academic_calendars'))
        request.user = mock.Mock()

        academic_calendar_form(request, self.academic_calendar_1.id)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'academic_calendar_form.html')
        self.assertIsInstance(context['form'], AcademicCalendarForm)

        data = {
            "academic_year": self.academic_year_1.pk,
            "title": "Academic event",
            "description": "Description of an academic event",
            "start_date": datetime.date.today(),
            "end_date": datetime.date.today() + datetime.timedelta(days=2)
        }

        request = request_factory.post(reverse('academic_calendars'), data)
        request.user = mock.Mock()
        academic_calendar_form(request, self.academic_calendar_1.id)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'academic_calendar_form.html')

