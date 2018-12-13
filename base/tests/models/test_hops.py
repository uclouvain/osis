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
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.models.hops import find_by_education_group_year
from base.tests.factories.hops import HopsFactory


class HopsTest(TestCase):
    def setUp(self):
        academic_year = AcademicYearFactory()
        self.education_group_yr = EducationGroupYearFactory(academic_year=academic_year)

    def test_find_by_education_group_year_None(self):
        self.assertIsNone(find_by_education_group_year(self.education_group_yr))

    def test_find_by_education_group_year(self):
        hops = HopsFactory(education_group_year=self.education_group_yr)
        self.assertEqual(find_by_education_group_year(self.education_group_yr), hops)
