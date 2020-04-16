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
import random

from django.test import TestCase
from base.tests.factories.education_group_year import EducationGroupYearFactory
from program_management.forms.program_version import _compute_url_used_in_dropdown_list_of_versions, \
    IDENTIFICATION_URL_NAME, _ordered_list
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory


class TestProgramVersionForm(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.education_group_year = EducationGroupYearFactory()

    def test_compute_url_with_standard(self):
        a_version = ProgramTreeVersionFactory(version_name='',
                                              is_transition=False,
                                              offer_id=self.education_group_year.id)
        an_url = _compute_url_used_in_dropdown_list_of_versions(IDENTIFICATION_URL_NAME, a_version)
        expected_url = "/educationgroups/{}/identification/".format(self.education_group_year.id)
        self.assertEqual(an_url, expected_url)

    def test_compute_url_with_standard_transition(self):
        a_version = ProgramTreeVersionFactory(version_name='',
                                              is_transition=True,
                                              offer_id=self.education_group_year.id)
        an_url = _compute_url_used_in_dropdown_list_of_versions(IDENTIFICATION_URL_NAME, a_version)
        expected_url = "/educationgroups/{}/transition/identification/".format(self.education_group_year.id)
        self.assertEqual(an_url, expected_url)

    def test_compute_url_with_particular(self):
        a_version = ProgramTreeVersionFactory(version_name='ICHEC',
                                              is_transition=False,
                                              offer_id=self.education_group_year.id)
        an_url = _compute_url_used_in_dropdown_list_of_versions(IDENTIFICATION_URL_NAME, a_version)
        expected_url = "/educationgroups/{}/{}/identification/".format(self.education_group_year.id, 'ICHEC')
        self.assertEqual(an_url, expected_url)

    def test_compute_url_with_particular_transition(self):
        a_version = ProgramTreeVersionFactory(version_name='ICHEC',
                                              is_transition=True,
                                              offer_id=self.education_group_year.id)
        an_url = _compute_url_used_in_dropdown_list_of_versions(IDENTIFICATION_URL_NAME, a_version)
        expected_url = "/educationgroups/{}/transition/{}/identification/".format(self.education_group_year.id, 'ICHEC')
        self.assertEqual(an_url, expected_url)

    def test_ordered_list(self):
        ichec_version = ProgramTreeVersionFactory(version_name='ICHEC',
                                                  is_transition=True,
                                                  offer_id=self.education_group_year.id)

        cems_transition_version = ProgramTreeVersionFactory(version_name='CEMS',
                                                            is_transition=True,
                                                            offer_id=self.education_group_year.id)

        cems_version = ProgramTreeVersionFactory(version_name='CEMS',
                                                 is_transition=False,
                                                 offer_id=self.education_group_year.id)
        standard_version = ProgramTreeVersionFactory(version_name='',
                                                     is_transition=False,
                                                     offer_id=self.education_group_year.id)
        standard_transition_version = ProgramTreeVersionFactory(version_name='',
                                                                is_transition=True,
                                                                offer_id=self.education_group_year.id)
        versions = [ichec_version, cems_transition_version, cems_version, standard_version, standard_transition_version]
        cpt = 0
        while cpt < 10:
            random.shuffle(versions)
            self.assertListEqual(
                _ordered_list(versions),
                [standard_version, standard_transition_version, cems_version, cems_transition_version, ichec_version]
            )
            cpt += 1

