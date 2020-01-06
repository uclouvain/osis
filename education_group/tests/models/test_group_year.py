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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.test import TestCase

from base.tests.factories.academic_year import AcademicYearFactory
from education_group.tests.factories.group import GroupFactory
from education_group.tests.factories.group_year import GroupYearFactory

ACRONYM = "ECON11BA"


class TestGroupYear(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year_1 = AcademicYearFactory()
        cls.academic_year_2 = AcademicYearFactory(year=cls.academic_year_1.year+1)

    def test_str_without_end_year(self):
        group_without_end_year = GroupFactory(start_year=self.academic_year_1,
                                              end_year=None)
        group_yr = GroupYearFactory(group=group_without_end_year, acronym=ACRONYM)
        self.assertEqual(str(group_yr),
                         "{} ({} - -)".format(group_yr.acronym,
                                              group_without_end_year.start_year.year))

    def test_str_with_end_year(self):
        group_with_end_year = GroupFactory(start_year=self.academic_year_1,
                                           end_year=self.academic_year_2)
        group_yr = GroupYearFactory(group=group_with_end_year, acronym=ACRONYM)
        self.assertEqual(str(group_yr),
                         "{} ({} - {})".format(group_yr.acronym,
                                               group_with_end_year.start_year.year,
                                               group_with_end_year.end_year.year))
