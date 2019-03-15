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
import re

from django.core.management import BaseCommand
from django.db.transaction import atomic

from base.models.admission_condition import AdmissionConditionLine


class Command(BaseCommand):
    """
    This command allow to clean placeholder data which contains year into
    # Placeholder data example: #prog:intitule:2017-min-lmath100i#
    """

    def add_arguments(self, parser):
        parser.add_argument('year', type=int, help='Specify the year to clean')

    @atomic
    def handle(self, *args, **options):
        field_to_sanitized = ['diploma', 'conditions', 'remarks', 'diploma_en', 'conditions_en', 'remarks_en']
        qs = AdmissionConditionLine.objects.filter(
            admission_condition__education_group_year__academic_year__year=options['year']
        ).only(*field_to_sanitized)

        for admission_condition_line in qs:
            for field in field_to_sanitized:
                text_cleaned = _sanitized_text(getattr(admission_condition_line, field, ''))
                setattr(admission_condition_line, field, text_cleaned)
            admission_condition_line.save()


def _sanitized_text(text):
    regex = r'(#\w*:\w*:)(\d{4}-)([\w-]*#)'
    for match in re.finditer(regex, text):
        placeholder_without_year = match.group(1) + match.group(3)
        text = text.replace(match.group(0), placeholder_without_year)
    return text
