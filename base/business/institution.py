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
from django.shortcuts import get_object_or_404

from base.models import entity_calendar, academic_year
from base.models.entity import Entity
from base.models.enums import academic_calendar_type
from base.models.person import Person


def find_summary_course_submission_dates_for_entity_version(entity_version):
    return entity_calendar.find_interval_dates_for_entity(
        ac_year=academic_year.current_academic_year(),
        reference=academic_calendar_type.SUMMARY_COURSE_SUBMISSION,
        entity=entity_version.entity
    )


def can_user_edit_educational_information_submission_dates_for_entity(a_user, an_entity):
    person = get_object_or_404(Person, user=a_user)
    return person.is_faculty_manager and person.is_attached_entities(Entity.objects.filter(pk=an_entity.pk))
