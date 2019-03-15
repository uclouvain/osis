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
from django.core.management import call_command, CommandError
from django.test import TestCase

from base.management.commands.clean_placeholder_reddot import _sanitized_text


class TestCleanPlaceholderCommand(TestCase):
    def test_clean_placeholder_command_case_no_year_provided(self):
        with self.assertRaises(CommandError):
            call_command('clean_placeholder_reddot')

    def test_clean_placeholder_command_case_year_not_integer(self):
        with self.assertRaises(CommandError):
            call_command('clean_placeholder_reddot', 'YEAR_STR')

    def test_clean_placeholder_command_case_success(self):
        call_command('clean_placeholder_reddot', 2018)


class TestSanitizedText(TestCase):
    def test_sanitized_text_case_no_placeholder_found_return_same_string(self):
        text = "Si l'étudiant a suivi le cours LDROI1200"
        self.assertEqual(_sanitized_text(text), text)

    def test_sanitized_text_case_placeholder_without_year_found_return_same_as_input(self):
        text = "Si l'étudiant a suivi la #prog:intitule:min-lmath100i#"
        self.assertEqual(_sanitized_text(text), text)

    def test_sanitized_text_case_one_placeholder_with_year_found(self):
        text = "Si l'étudiant a suivi la #prog:intitule:2017-min-lmath100i#"
        expected_result = "Si l'étudiant a suivi la #prog:intitule:min-lmath100i#"
        self.assertEqual(_sanitized_text(text), expected_result)

    def test_sanitized_text_case_multiple_placeholder_with_year_found(self):
        text = "Si l'étudiant a suivi la #prog:intitule:2017-min-lmath100i# #prog:intitule:2017-lagr100a# alors ok"
        expected_result = "Si l'étudiant a suivi la #prog:intitule:min-lmath100i# #prog:intitule:lagr100a# alors ok"
        self.assertEqual(_sanitized_text(text), expected_result)
