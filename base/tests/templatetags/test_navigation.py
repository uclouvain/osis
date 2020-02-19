############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
import urllib

from django.http import QueryDict
from django.test import TestCase
from django.urls import reverse

from base.templatetags import navigation
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory


class TestNavigationEducationGroupYear(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(current=True)
        education_group_years = EducationGroupYearFactory.create_batch(5, academic_year=cls.academic_year)
        cls.education_group_years_sorted_by_acronym = sorted(education_group_years, key=lambda obj: obj.acronym)

    def setUp(self):
        self.query_parameters = QueryDict(mutable=True)
        self.query_parameters["search_query"] = urllib.parse.quote_plus(
            'academic_year={academic_year}&ordering=acronym'.format(
                academic_year=self.academic_year.id
            )
        )

    def test_navigation_when_no_search_query(self):
        context = navigation.navigation(QueryDict(), self.education_group_years_sorted_by_acronym[0])
        expected_context = {
            "current_element": self.education_group_years_sorted_by_acronym[0]
        }
        self.assertDictEqual(
            context,
            expected_context
        )

    def test_first_element_should_not_have_previous_element(self):
        first_element_index = 0
        expected_context = {
            "current_element": self.education_group_years_sorted_by_acronym[first_element_index],
            "next_element": self.education_group_years_sorted_by_acronym[first_element_index + 1],
            "next_url": self._get_element_url(self.query_parameters, first_element_index + 1),
            "previous_element": None,
            "previous_url": None,
        }
        self.assertNavigationContextEquals(expected_context, first_element_index)

    def test_last_element_should_not_have_next_element(self):
        last_element_index = len(self.education_group_years_sorted_by_acronym) - 1
        expected_context = {
            "current_element": self.education_group_years_sorted_by_acronym[last_element_index],
            "next_element": None,
            "next_url": None,
            "previous_element": self.education_group_years_sorted_by_acronym[last_element_index - 1],
            "previous_url": self._get_element_url(self.query_parameters, last_element_index - 1),
        }
        self.assertNavigationContextEquals(expected_context, last_element_index)

    def test_inner_element_should_have_previous_and_next_element(self):
        inner_element_index = 2
        expected_context = {
            "current_element": self.education_group_years_sorted_by_acronym[inner_element_index],
            "next_element": self.education_group_years_sorted_by_acronym[inner_element_index + 1],
            "next_url": self._get_element_url(self.query_parameters, inner_element_index + 1),
            "previous_element": self.education_group_years_sorted_by_acronym[inner_element_index - 1],
            "previous_url": self._get_element_url(self.query_parameters, inner_element_index - 1),
        }
        self.assertNavigationContextEquals(expected_context, inner_element_index)

    def assertNavigationContextEquals(self, expected_context, index):
        self.query_parameters["index"] = index
        context = navigation.navigation(self.query_parameters, self.education_group_years_sorted_by_acronym[index])
        self.assertDictEqual(
            context,
            expected_context
        )

    def _get_element_url(self, query_parameters: QueryDict, index):
        query_parameters_with_updated_index = QueryDict(mutable=True)
        query_parameters_with_updated_index.update(query_parameters)
        query_parameters_with_updated_index["index"] = index

        next_element = self.education_group_years_sorted_by_acronym[index]

        return "{}?{}".format(
            reverse("education_group_read", args=[next_element.id, next_element.id]),
            query_parameters_with_updated_index.urlencode()
        )
