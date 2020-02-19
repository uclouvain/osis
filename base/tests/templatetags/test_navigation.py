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


class TestNavigation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(current=True)

    def test_navigation_for_education_group_year(self):
        education_group_parent = EducationGroupYearFactory(acronym="Parent", academic_year=self.academic_year)
        education_group_child_1 = EducationGroupYearFactory(acronym="Child_1", academic_year=self.academic_year)
        education_group_child_2 = EducationGroupYearFactory(acronym="Child_2", academic_year=self.academic_year)

        query_parameters = QueryDict(mutable=True)
        query_parameters["search_query"] = urllib.parse.quote_plus(
            'academic_year={academic_year}&ordering=acronym'.format(
                academic_year=self.academic_year.id
            )
        )
        query_parameters["index"] = 0

        context = navigation.navigation(query_parameters, education_group_child_1)

        self.assertEqual(
            context["next_element"],
            education_group_child_2
        )
        query_parameters["index"] = 1
        self.assertEqual(
            context["next_url"],
            "{}?{}".format(
                reverse("education_group_read", args=[education_group_child_2.id, education_group_child_2.id]),
                query_parameters.urlencode()
            )
        )
        self.assertIsNone(
            context["previous_element"]
        )
        self.assertIsNone(
            context["previous_url"],

        )
        self.assertEqual(
            context["index"],
            0
        )
