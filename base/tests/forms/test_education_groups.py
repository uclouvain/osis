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

from django.test import TestCase

from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.forms.education_groups import EducationGroupFilter
from django.utils.translation import ugettext_lazy as _
from base.models.education_group_type import EducationGroupType


class TestEducationGroupTypeOrderingForm(TestCase):

    def setUp(self):
        self.educ_grp_type_D = EducationGroupTypeFactory(name='D label')
        self.educ_grp_type_B = EducationGroupTypeFactory(name='B label')
        self.educ_grp_type_A = EducationGroupTypeFactory(name='A label')

        self.form = EducationGroupFilter()
        self.form.fields["education_group_type"].queryset = EducationGroupType.objects.all().order_by_translated_name()

    def test_ordering(self):
        self.assertEqual(list(self.form.fields["education_group_type"].queryset),
                         [self.educ_grp_type_A, self.educ_grp_type_B, self.educ_grp_type_D])
        educ_grp_type_C = EducationGroupTypeFactory(name='C label')
        self.form.fields["education_group_type"].queryset = EducationGroupType.objects.all().order_by_translated_name()
        self.assertEqual(
            list(self.form.fields["education_group_type"].queryset),
            [self.educ_grp_type_A, self.educ_grp_type_B, educ_grp_type_C, self.educ_grp_type_D]
        )
