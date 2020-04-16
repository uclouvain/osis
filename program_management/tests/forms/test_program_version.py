############################################################################
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
############################################################################
from django.test import TestCase

from program_management.forms.program_version import _compute_url_used_in_dropdown_list_of_versions, IDENTIFICATION_URL_NAME

EDUCATION_GROUP_YR_ID = 1


class TestProgramVersionForm(TestCase):
    def test_compute_url_with_standard(self):
        an_url = _compute_url_used_in_dropdown_list_of_versions(IDENTIFICATION_URL_NAME, '', False, EDUCATION_GROUP_YR_ID)
        expected_url = "/educationgroups/{}/identification/".format(EDUCATION_GROUP_YR_ID)
        self.assertEqual(an_url, expected_url)

    def test_compute_url_with_standard_transition(self):
        an_url = _compute_url_used_in_dropdown_list_of_versions(IDENTIFICATION_URL_NAME, '', True, EDUCATION_GROUP_YR_ID)
        expected_url = "/educationgroups/{}/transition/identification/".format(EDUCATION_GROUP_YR_ID)
        self.assertEqual(an_url, expected_url)

    def test_compute_url_with_particular(self):
        an_url = _compute_url_used_in_dropdown_list_of_versions(IDENTIFICATION_URL_NAME, 'ICHEC', False, EDUCATION_GROUP_YR_ID)
        expected_url = "/educationgroups/{}/{}/identification/".format(EDUCATION_GROUP_YR_ID, 'ICHEC')
        self.assertEqual(an_url, expected_url)

    def test_compute_url_with_particular_transition(self):
        an_url = _compute_url_used_in_dropdown_list_of_versions(IDENTIFICATION_URL_NAME, 'ICHEC', True, EDUCATION_GROUP_YR_ID)
        expected_url = "/educationgroups/{}/transition/{}/identification/".format(EDUCATION_GROUP_YR_ID, 'ICHEC')
        self.assertEqual(an_url, expected_url)

