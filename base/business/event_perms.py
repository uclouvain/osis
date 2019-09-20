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
from abc import ABC

from django.utils.translation import ugettext_lazy as _

from base.business.education_groups import perms
from base.models.academic_calendar import get_academic_calendar_by_date_and_reference_and_data_year, AcademicCalendar
from base.models.enums import academic_calendar_type


class EventPerm(ABC):
    @classmethod
    def is_open(cls, *args, **kwargs):
        if kwargs.get('education_group'):
            return cls.__is_open_for_spec_egy(*args, **kwargs)
        return cls.__is_open_other_rules(*args, **kwargs)

    @staticmethod
    def __is_open_for_spec_egy(*args, **kwargs):
        return False

    @staticmethod
    def __is_open_other_rules(*args, **kwargs):
        return False


class EventPermDeliberation(EventPerm):
    pass


class EventPermDissertationSubmission(EventPerm):
    pass


class EventPermExamEnrollment(EventPerm):
    pass


class EventPermScoresExamDiffusion(EventPerm):
    pass


class EventPermScoresExamSubmission(EventPerm):
    pass


class EventPermTeachingChargeApplication(EventPerm):
    pass


class EventPermCourseEnrollment(EventPerm):
    pass


class EventPermSummaryCourseSubmission(EventPerm):
    pass


class EventPermEducationGroupEdition(EventPerm):
    @staticmethod
    def __is_open_for_spec_egy(*args, **kwargs):
        aca_year = kwargs.get('education_group').academic_year
        academic_calendar = get_academic_calendar_by_date_and_reference_and_data_year(
            aca_year, academic_calendar_type.EDUCATION_GROUP_EDITION)
        error_msg = None
        if not academic_calendar:
            error_msg = _("This education group is not editable during this period.")

        result = error_msg is None
        perms.can_raise_exception(kwargs.get('raise_exception', False), result, error_msg)
        return result if kwargs.get('raise_exception', False) else academic_calendar

    @staticmethod
    def __is_calendar_opened(*args, **kwargs):
        return AcademicCalendar.objects.open_calendars()\
            .filter(reference=academic_calendar_type.EDUCATION_GROUP_EDITION)\
            .exists()
